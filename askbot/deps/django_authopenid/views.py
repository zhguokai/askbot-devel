# -*- coding: utf-8 -*-
# Copyright (c) 2007, 2008, Benoît Chesneau
# Copyright (c) 2007 Simon Willison, original work on django-openid
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#      * Redistributions of source code must retain the above copyright
#      * notice, this list of conditions and the following disclaimer.
#      * Redistributions in binary form must reproduce the above copyright
#      * notice, this list of conditions and the following disclaimer in the
#      * documentation and/or other materials provided with the
#      * distribution.  Neither the name of the <ORGANIZATION> nor the names
#      * of its contributors may be used to endorse or promote products
#      * derived from this software without specific prior written
#      * permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import cgi
import datetime
from django.http import HttpResponseRedirect, Http404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.template import RequestContext, Context
from django.conf import settings as django_settings
from askbot.conf import settings as askbot_settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.core import exceptions as django_exceptions
from django.core.context_processors import csrf as csrf_context
from django.core.urlresolvers import reverse
from django.forms.util import ErrorList
from django.shortcuts import render
from django.template.loader import get_template
from django.views.decorators import csrf
from django.utils.encoding import smart_unicode
from django.utils import simplejson
from askbot.utils.functions import generate_random_key
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from askbot import exceptions as askbot_exceptions
from askbot.mail import send_mail
from askbot.utils import decorators as askbot_decorators
from askbot.utils.html import site_url
from recaptcha_works.decorators import fix_recaptcha_remote_ip
from askbot.deps.django_authopenid.ldap_auth import ldap_create_user
from askbot.deps.django_authopenid.ldap_auth import ldap_authenticate
from askbot.mail import send_email_key
from askbot.skins.loaders import render_to_string
from askbot.utils.decorators import ajax_only
from askbot.utils.decorators import post_only
from askbot.utils.html import split_contents_and_scripts
from askbot.utils.http import render_to_json_response
from askbot.utils.loading import load_module
from sanction.client import Client as OAuth2Client
from urlparse import urlparse

from openid.consumer.consumer import Consumer, \
    SUCCESS, CANCEL, FAILURE, SETUP_NEEDED
from openid.consumer.discover import DiscoveryFailure
from openid.extensions import sreg
# needed for some linux distributions like debian
try:
    from openid.yadis import xri
except ImportError:
    from yadis import xri

try:
    from xmlrpclib import Fault as WpFault
    from wordpress_xmlrpc import Client
    from wordpress_xmlrpc.methods.users import GetUserInfo
except ImportError:
    pass


import urllib
from askbot import forms as askbot_forms
from askbot.deps.django_authopenid import util
from askbot.deps.django_authopenid import decorators
from askbot.deps.django_authopenid.models import UserAssociation, UserEmailVerifier
from askbot.deps.django_authopenid import forms
from askbot.deps.django_authopenid.backends import AuthBackend
import logging
from askbot.utils.forms import get_next_url
from askbot.utils.forms import get_feed
from askbot.utils.http import get_request_info
from askbot.models.signals import user_logged_in, user_registered

def close_modal_menu(request):
    """clears session variables related to the modal menu"""
    request.session.pop('modal_menu', None)

def create_authenticated_user_account(
    username=None, email=None, password=None,
    user_identifier=None, login_provider_name=None
):
    """creates a user account, user association with
    the login method and the the default email subscriptions
    """

    user = User.objects.create_user(username, email)
    user_registered.send(None, user=user)

    logging.debug('creating new openid user association for %s', username)

    if password:
        user.set_password(password)
        user.save()
    else:
        UserAssociation(
            openid_url = user_identifier,
            user = user,
            provider_name = login_provider_name,
            last_used_timestamp = datetime.datetime.now()
        ).save()

    subscribe_form = askbot_forms.SimpleEmailSubscribeForm({'subscribe': 'y'})
    subscribe_form.full_clean()
    logging.debug('saving email feed settings')
    subscribe_form.save(user)

    logging.debug('logging the user in')
    user = authenticate(method='force', user_id=user.id)
    if user is None:
        error_message = 'please make sure that ' + \
                        'askbot.deps.django_authopenid.backends.AuthBackend' + \
                        'is in your settings.AUTHENTICATION_BACKENDS'
        raise Exception(error_message)

    return user


def cleanup_post_register_session(request):
    """delete keys from session after registration is complete"""
    keys = (
        'user_identifier',
        'login_provider_name',
        'username',
        'email',
        'password',
        'validation_code'
    )
    for key in keys:
        if key in request.session:
            del request.session[key]


#todo: decouple from askbot
def login(request, user):
    
    if user.is_blocked():
        message = askbot_settings.BLOCKED_USER_LOGIN_MESSAGE
        request.user.message_set.create(message=message)
        return
    
    from django.contrib.auth import login as _login

    # get old session key
    session_key = request.session.session_key

    # login and get new session key
    _login(request, user)

    # send signal with old session key as argument
    logging.debug('logged in user %s with session key %s' % (user.username, session_key))
    #todo: move to auth app
    user_logged_in.send(
        request = request, user = user, session_key=session_key, sender=None
    )

#todo: uncouple this from askbot
def logout(request):
    from django.contrib.auth import logout as _logout#for login I've added wrapper below - called login
    if 'openid' in request.session:
        del request.session['openid']
    _logout(request)

def logout_page(request):
    data = {
        'page_class': 'meta',
        'have_federated_login_methods': util.have_enabled_federated_login_methods()
    }
    return render(request, 'authopenid/logout.html', data)

def get_logged_in_user_data(request, user):
    """returns a dictionary with the user data html snippet
    for the header"""
    html = render_to_string(request, 'widgets/user_navigation.html')
    #using a patched variable for the url of a post entered before login
    if askbot_settings.ASKBOT_CLOSED_FORUM_MODE:
        url = get_next_url(request, default=django_settings.LOGIN_REDIRECT_URL)
    else:
        url = getattr(user, '_askbot_new_post_url', None)
    return {'userToolsNavHTML': html, 'redirectUrl': url}

def get_url_host(request):
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    host = escape(request.get_host())
    return '%s://%s' % (protocol, host)

def get_full_url(request):
    return get_url_host(request) + request.get_full_path()

def ask_openid(
            request,
            openid_url,
            redirect_to,
            sreg_request=None
        ):
    """ basic function to ask openid and return response """
    trust_root = getattr(
        django_settings, 'OPENID_TRUST_ROOT', get_url_host(request) + '/'
    )
    if xri.identifierScheme(openid_url) == 'XRI' and getattr(
            django_settings, 'OPENID_DISALLOW_INAMES', False
    ):
        msg = _("i-names are not supported")
        logging.debug('openid failed because i-names are not supported')
        return signin_failure(request, msg)
    consumer = Consumer(request.session, util.DjangoOpenIDStore())
    try:
        auth_request = consumer.begin(openid_url)
    except DiscoveryFailure:
        openid_url = cgi.escape(openid_url)
        msg = _(u"OpenID %(openid_url)s is invalid" % {'openid_url':openid_url})
        logging.debug(msg)
        return signin_failure(request, msg)

    logging.debug('openid seemed to work')
    if sreg_request:
        logging.debug('adding sreg_request - wtf it is?')
        auth_request.addExtension(sreg_request)
    redirect_url = auth_request.redirectURL(trust_root, redirect_to)
    logging.debug('redirecting to %s' % redirect_url)
    return HttpResponseRedirect(redirect_url)

def complete(request, return_to=None):
    """ complete openid signin """
    logging.debug('in askbot.deps.django_authopenid.complete')

    consumer = Consumer(request.session, util.DjangoOpenIDStore())
    # make sure params are encoded in utf8
    params = dict((k,smart_unicode(v)) for k, v in request.GET.items())
    openid_response = consumer.complete(params, return_to)

    try:
        logging.debug(u'returned openid parameters were: %s' % unicode(params))
    except Exception, e:
        logging.critical(u'fix logging statement above ' + unicode(e))

    if openid_response.status == SUCCESS:
        logging.debug('openid response status is SUCCESS')
        return signin_success(
                    request,
                    openid_response.identity_url,
                    openid_response
                )
    elif openid_response.status == CANCEL:
        logging.debug('CANCEL')
        return signin_failure(request, 'The request was canceled')
    elif openid_response.status == FAILURE:
        logging.debug('FAILURE')
        return signin_failure(request, openid_response.message)
    elif openid_response.status == SETUP_NEEDED:
        logging.debug('SETUP NEEDED')
        return signin_failure(request, 'Setup needed')
    else:
        logging.debug('BAD OPENID STATUS')
        assert False, "Bad openid status: %s" % openid_response.status

def not_authenticated(func):
    """ decorator that redirect user to next page if
    he/she is already logged in."""
    def decorated(request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(get_next_url(request))
        return func(request, *args, **kwargs)
    return decorated

def complete_oauth2_signin(request):
    if 'next_url' in request.session:
        next_url = request.session['next_url']
        del request.session['next_url']
    else:
        next_url = reverse('index')

    if 'error' in request.GET:
        return HttpResponseRedirect(reverse('index'))

    csrf_token = request.GET.get('state', None)
    oauth2_csrf_token = request.session.pop('oauth2_csrf_token', None)
    if csrf_token is None or csrf_token != oauth2_csrf_token:
        return HttpResponseBadRequest()

    providers = util.get_enabled_login_providers()
    provider_name = request.session.pop('provider_name')
    params = providers[provider_name]
    assert(params['type'] == 'oauth2')

    name_token = provider_name.replace('-', '_').upper()
    client_id = getattr(
            askbot_settings,
            name_token + '_KEY',
        )

    client_secret = getattr(
            askbot_settings,
            name_token + '_SECRET',
        )

    client = OAuth2Client(
            token_endpoint=params['token_endpoint'],
            resource_endpoint=params['resource_endpoint'],
            redirect_uri=site_url(reverse('user_complete_oauth2_signin')),
            client_id=client_id,
            client_secret=client_secret,
            token_transport=params.get('token_transport', None)
        )

    client.request_token(
        code=request.GET['code'],
        parser=params.get('response_parser', None)
    )

    #todo: possibly set additional parameters here
    user_id = params['get_user_id_function'](client)

    user = authenticate(
                oauth_user_id=user_id,
                provider_name=provider_name,
                method='oauth'
            )

    logging.debug('finalizing oauth signin')

    request.session['email'] = ''#todo: pull from profile
    request.session['username'] = ''#todo: pull from profile

    if provider_name == 'facebook':
        profile = client.request("me")
        request.session['email'] = profile.get('email', '')
        request.session['username'] = profile.get('username', '')
    elif provider_name == 'google-plus' and user is None:
        #attempt to migrate user from the old OpenId protocol
        openid_url = getattr(client, 'openid_id', None)
        if openid_url:
            msg_tpl = 'trying to migrate user %d from OpenID %s to g-plus %s'
            logging.critical(msg_tpl, (user.id, str(openid_url), str(user_id)))
            user = authenticate(openid_url=openid_url)
            if user:
                util.google_migrate_from_openid_to_gplus(openid_url, user_id)
                logging.critical('migrated login from OpenID to g-plus')


    return finalize_generic_signin(
                        request = request,
                        user = user,
                        user_identifier = user_id,
                        login_provider_name = provider_name
                    )



def complete_oauth_signin(request):
    """this view will set type of modal menu to
    load and will forward to the previous
    referrer url, so that user is at the same
    page where he/she started logging in"""
    if 'next_url' in request.session:
        next_url = request.session['next_url']
        del request.session['next_url']
    else:
        next_url = reverse('index')

    #todo: make modal menues work here
    if 'denied' in request.GET:
        #todo: populate
        #request.session['modal_menu']
        #context = {'title': _('OAuth login canceled')}
        return HttpResponseRedirect(next_url)
    if 'oauth_problem' in request.GET:
        #todo: populate
        #request.session['modal_menu']
        #context = {'title': _('OAuth login canceled')}
        return HttpResponseRedirect(next_url)

    try:
        oauth_token = request.GET['oauth_token']
        logging.debug('have token %s' % oauth_token)
        oauth_verifier = request.GET['oauth_verifier']
        logging.debug('have verifier %s' % oauth_verifier)
        session_oauth_token = request.session['oauth_token']
        logging.debug('have token from session')
        assert(oauth_token == session_oauth_token['oauth_token'])

        oauth_provider_name = request.session['oauth_provider_name']
        logging.debug('have saved provider name')
        del request.session['oauth_provider_name']

        oauth = util.OAuthConnection(oauth_provider_name)

        user_id = oauth.get_user_id(
                                oauth_token = session_oauth_token,
                                oauth_verifier = oauth_verifier
                            )
        logging.debug('have %s user id=%s' % (oauth_provider_name, user_id))

        user = authenticate(
                    oauth_user_id = user_id,
                    provider_name = oauth_provider_name,
                    method = 'oauth'
                )

        logging.debug('finalizing oauth signin')

        request.session['email'] = ''#todo: pull from profile
        request.session['username'] = ''#todo: pull from profile

        return finalize_generic_signin(
                            request = request,
                            user = user,
                            user_identifier = user_id,
                            login_provider_name = oauth_provider_name
                        )

    except Exception, e:
        logging.critical(e)
        msg = _('Sorry, there was some problem '
                'connecting to the login provider, please try again '
                'or use another login method'
            )
        request.user.message_set.create(message = msg)
        return HttpResponseRedirect(next_url)

@csrf.csrf_protect
@ajax_only
@post_only
def change_password(request):
    user = request.user
    if user.is_anonymous():
        return HttpResponseForbidden()

    post_data = simplejson.loads(request.raw_post_data)
    form = forms.SetPasswordForm(post_data)
    if form.is_valid():
        password = form.cleaned_data['password1']
        user.set_password(password)
        user.save()
        return {'message': _('Your new password saved')}
    else:
        return {'errors': form.errors}


@csrf.csrf_protect
@post_only
def ldap_signin(request):
    """sign in or create an account with LDAP"""

    login_form = forms.ClassicLoginForm(request.POST)
    #todo: clean the form
    username = login_form.cleaned_data['username']
    password = login_form.cleaned_data['password']

    user = authenticate(
                    username=username,
                    password=password,
                    method = 'ldap'
                )

    if user:
        login(request, user)
        return get_logged_in_user_data(request, user)
    else:
        #try to login again via LDAP
        user_info = ldap_authenticate(username, password)
        if user_info['success']:
            if askbot_settings.LDAP_AUTOCREATE_USERS:
                #create new user or
                user = ldap_create_user(user_info).user
                user = authenticate(method='force', user_id=user.id)
                assert(user is not None)
                login(request, user)
                return get_logged_in_user_data(request, user)
            else:
                #continue with proper registration
                ldap_username = user_info['ldap_username']
                request.session['email'] = user_info['email']
                request.session['ldap_user_info'] = user_info
                if askbot_settings.AUTOFILL_USER_DATA:
                    request.session['username'] = ldap_username
                    request.session['first_name'] = \
                        user_info['first_name']
                    request.session['last_name'] = \
                        user_info['last_name']
                else:
                    #clean up the session dict - we don't want these items to be there
                    request.session.pop('username', None)
                    request.session.pop('first_name', None)
                    request.session.pop('last_name', None)
                return finalize_generic_signin(
                    request,
                    login_provider_name = 'ldap',
                    user_identifier = ldap_username + '@ldap'
                )
        else:
            auth_fail_func_path = getattr(
                                django_settings,
                                'LDAP_AUTHENTICATE_FAILURE_FUNCTION',
                                None
                            )

            if auth_fail_func_path:
                auth_fail_func = load_module(auth_fail_func_path)
                auth_fail_func(user_info, login_form)
            else:
                login_form.set_password_login_error(user_info.get('error_info'))


@csrf.csrf_protect
@ajax_only
@post_only
def password_signin(request):
    #password_action = login_form.cleaned_data['password_action']
    post_data = simplejson.loads(request.raw_post_data)
    form = forms.ClassicLoginForm(post_data)
    if form.is_valid():
        user = authenticate(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password'],
                provider_name = 'local',
                method = 'password'
            )
        if user:
            login(request, user)
            #todo: here we might need to set cookies
            #for external login sites
            #get user tools nav login snippet
            return get_logged_in_user_data(request, user)
        return {'errors': {'username': [_('Login failed, please try again')]}}
    else:
        return {'errors': form.errors}

#@not_authenticated
@csrf.csrf_protect
def signin(request, template_name='authopenid/signin_full.html'):
    """
    signin page. It manages the legacy authentification (user/password)
    and openid authentification

    url: /signin/

    template : authopenid/signin.htm

    returns either a json dictionary or raises an exception
    dictionary may have fields:
    * html (html of the form)
    * message (any messages to flash to the user)
    * user data: id, username, reputation, xxx_badges_count (xxx in (gold, silver, bronze))
    """
    logging.debug('in signin view')
    #we need a special priority on where to redirect on successful login
    #here:
    #1) url parameter "next" - if explicitly set
    #2) url from django setting LOGIN_REDIRECT_URL
    #3) home page of the forum

    #todo: decide how to set next_url
    login_redirect_url = getattr(django_settings, 'LOGIN_REDIRECT_URL', None)
    next_url = get_next_url(request, default=login_redirect_url, form_prefix='login')
    logging.debug('next url is %s' % next_url)

    if askbot_settings.ALLOW_ADD_REMOVE_LOGIN_METHODS == False \
        and request.user.is_authenticated():
        raise django_exceptions.PermissionDenied()

    #this is a trap for the signin page used to validate logins
    if next_url == reverse('user_signin'):
        next_url = '%(next)s?next=%(next)s' % {'next': next_url}

    #need this to keep users on the same page after third party registration
    #unless rererer is the signin page
    if 'HTTP_REFERER' in request.META:
        referer = request.META['HTTP_REFERER']
        if urlparse(referer).path != reverse('widget_signin'):
            request.session['next_url'] = referer

    #todo: get next url make it sticky if next is 'user_signin'
    if request.method == 'GET':
        #render full page signin view
        if request.is_ajax():
            return get_signin_view_data(request, 'authopenid/signin.html')
        else:
            return get_signin_view(request, template_name=template_name)
    else:
        login_form = forms.LoginForm(request.POST, prefix='login')
        if login_form.is_valid():
            provider_name = login_form.cleaned_data['login_provider_name']

            if login_form.cleaned_data['login_type'] == 'mozilla-persona':
                assertion = login_form.cleaned_data['persona_assertion']
                email = util.mozilla_persona_get_email_from_assertion(assertion)
                if email:
                    user = authenticate(email=email, method='mozilla-persona')
                    if user is None:
                        user = authenticate(email=email, method='valid_email')
                        if user:
                            #create mozilla persona user association
                            #because we trust the given email address belongs
                            #to the same user
                            UserAssociation(
                                openid_url=email,
                                user=user,
                                provider_name='mozilla-persona',
                                last_used_timestamp=datetime.datetime.now()
                            ).save()

                    if user:
                        login(request, user)
                        return HttpResponseRedirect(next_url)
                    #else - create new user account
                    #pre-fill email address with persona registration
                    request.session['email'] = email
                    return finalize_generic_signin(
                        request,
                        login_provider_name = 'mozilla-persona',
                        user_identifier = email
                    )
                    
            elif login_form.cleaned_data['login_type'] == 'openid':
                #initiate communication process
                logging.debug('processing signin with openid submission')

                #todo: make a simple-use wrapper for openid protocol

                sreg_req = sreg.SRegRequest(optional=['nickname', 'email'])
                next_url = login_form.cleaned_data['next']
                url_params = {
                    'next': next_url,
                    'space': get_feed(request)#todo make work w/o spaces
                }
                redirect_to = "%s%s?%s" % (
                        get_url_host(request),
                        reverse('user_complete_signin'),
                        urllib.urlencode(url_params)
                )
                return ask_openid(
                            request,
                            login_form.cleaned_data['openid_url'],
                            redirect_to,
                            sreg_request=sreg_req
                        )

            elif login_form.cleaned_data['login_type'] == 'oauth':
                try:
                    #this url may need to have "next" piggibacked onto
                    connection = util.OAuthConnection(
                                    provider_name,
                                    callback_url=reverse('user_complete_oauth_signin')
                                )

                    connection.start()

                    request.session['oauth_token'] = connection.get_token()
                    request.session['oauth_provider_name'] = provider_name
                    request.session['next_url'] = next_url#special case for oauth

                    oauth_url = connection.get_auth_url(login_only=True)
                    return HttpResponseRedirect(oauth_url)

                except util.OAuthError, e:
                    logging.critical(unicode(e))
                    msg = _('Unfortunately, there was some problem when '
                            'connecting to %(provider)s, please try again '
                            'or use another provider'
                        ) % {'provider': provider_name}
                    raise askbot_exceptions.AuthProviderError(msg)

            elif login_form.cleaned_data['login_type'] == 'oauth2':
                try:
                    csrf_token = generate_random_key(length=32)
                    redirect_url = util.get_oauth2_starter_url(provider_name, csrf_token)
                    request.session['oauth2_csrf_token'] = csrf_token
                    request.session['provider_name'] = provider_name
                    return HttpResponseRedirect(redirect_url)
                except util.OAuthError, e:
                    logging.critical(unicode(e))
                    msg = _('Unfortunately, there was some problem when '
                            'connecting to %(provider)s, please try again '
                            'or use another provider'
                        ) % {'provider': provider_name}
                    request.user.message_set.create(message = msg)

            elif login_form.cleaned_data['login_type'] == 'wordpress_site':
                #here wordpress_site means for a self hosted wordpress blog not a wordpress.com blog
                wp = Client(
                        askbot_settings.WORDPRESS_SITE_URL,
                        login_form.cleaned_data['username'],
                        login_form.cleaned_data['password']
                    )
                try:
                    wp_user = wp.call(GetUserInfo())
                    custom_wp_openid_url = '%s?user_id=%s' % (wp.url, wp_user.user_id)
                    user = authenticate(
                            method = 'wordpress_site',
                            wordpress_url = wp.url,
                            wp_user_id = wp_user.user_id
                           )
                    return finalize_generic_signin(
                                    request = request,
                                    user = user,
                                    user_identifier = custom_wp_openid_url,
                                    login_provider_name = provider_name,
                                )
                except WpFault, e:
                    logging.critical(unicode(e))
                    msg = _('The login password combination was not correct')
                    raise askbot_exceptions.AuthProviderError(msg)
            else:
                #raise 500 error - unknown login type
                pass
        else:
            #invalid form branch, should not normally get here
            logging.debug('login form is not valid')
            logging.debug(login_form.errors)
            logging.debug(request.REQUEST)
            json_data = simplejson.dumps(
                {'errors': login_form.errors, 'success': True}
            )
            return HttpResponse(json_data, mimetype='application/json')

def get_signin_view_context(request):
    """url-less utility function that populates
    context of template 'authopenid/signin.html'
    and returns its rendered output
    """

    #todo: this stuff should be injected by js when the modal menu is open
    #because askbot should have nothing to do with the login app
    from askbot.models import AnonymousQuestion as AQ
    session_key = request.session.session_key
    logging.debug('retrieving anonymously posted question associated with session %s' % session_key)
    qlist = AQ.objects.filter(session_key=session_key).order_by('-added_at')
    if len(qlist) > 0:
        question = qlist[0]
    else:
        question = None

    from askbot.models import AnonymousAnswer as AA
    session_key = request.session.session_key
    logging.debug('retrieving posted answer associated with session %s' % session_key)
    alist = AA.objects.filter(session_key=session_key).order_by('-added_at')
    if len(alist) > 0:
        answer = alist[0]
    else:
        answer = None

    if request.user.is_authenticated():
        users_login_methods = UserAssociation.objects.filter(user = request.user)
        #annotate objects with extra data
        providers = util.get_enabled_login_providers()
        for login_method in users_login_methods:
            try:
                provider_data = providers[login_method.provider_name]
                if provider_data['type'] == 'password':
                    #only external password logins will not be deletable
                    #this is because users with those can lose access to their accounts permanently
                    login_method.is_deletable = provider_data.get('password_changeable', False)
                else:
                    login_method.is_deletable = True
            except KeyError:
                logging.critical(
                    'login method %s is no longer available '
                    'please delete records for this login method '
                    'from the UserAssociation table',
                    login_method.provider_name
                )
                continue
    else:
        users_login_methods = list()

    next_url = get_next_url(request)
    login_form = forms.LoginForm(initial={'next': next_url}, prefix='login')
    data = {
        'account_recovery_form': forms.AccountRecoveryForm(prefix='recover'),
        'answer': answer,
        'login_form': login_form,
        'openid_error_message': request.REQUEST.get('msg',''),
        'page_class': 'openid-signin',
        'password_register_form': forms.ClassicRegisterForm(prefix='register'),
        'password_login_form': forms.ClassicLoginForm(prefix='login'),
        'question': question,
        'use_password_login': util.use_password_login()
    }

    login_providers = util.get_enabled_login_providers()

    #determine if we are only using password login
    active_provider_names = [p['name'] for p in login_providers.values()]

    data['have_buttons'] = len(active_provider_names)

    if request.user.is_authenticated():
        data['existing_login_methods'] = users_login_methods
        active_provider_names = [item.provider_name for item in users_login_methods]
    else:
        active_provider_names = list()
        
    util.set_login_provider_tooltips(login_providers, active_provider_names)

    data['login_providers'] = login_providers.values()
    data.update(csrf_context(request))

    data['feed'] = get_feed(request)
    return data

def get_signin_view(request, template_name='authopenid/signin_full.html'):
    data = get_signin_view_context(request)
    close_modal_menu(request)#don't allow modal menues on this page
    return render(request, template_name, data)


@csrf.csrf_protect
@ajax_only
def get_signin_view_data(request, template_name='authopenid/signin.html'):
    data = get_signin_view_context(request)
    signin_view_html = render_to_string(request, template_name, data)
    scripts_html = render_to_string(
                request, 'authopenid/providers_javascript.html', data
            )
    junk, scripts = split_contents_and_scripts(scripts_html)
    return {'html': signin_view_html, 'scripts': scripts}

@login_required
@csrf.csrf_protect
def delete_login_method(request):
    if askbot_settings.ALLOW_ADD_REMOVE_LOGIN_METHODS == False:
        raise Http404
    if request.is_ajax() and request.method == 'POST':
        provider_name = request.POST['provider_name']
        try:
            login_method = UserAssociation.objects.get(
                                                user = request.user,
                                                provider_name = provider_name
                                            )
            login_method.delete()
            return HttpResponse('', mimetype = 'application/json')
        except UserAssociation.DoesNotExist:
            #error response
            message = _('Login method %(provider_name)s does not exist')
            return HttpResponse(message, status=500, mimetype = 'application/json')
        except UserAssociation.MultipleObjectsReturned:
            logging.critical(
                    'have multiple %(provider)s logins for user %(id)s'
                ) % {'provider':provider_name, 'id': request.user.id}
            message = _('Oops, sorry - there was some error - please try again')
            return HttpResponse(message, status=500, mimetype = 'application/json')
    else:
        raise Http404

def complete_signin(request):
    """ in case of complete signin with openid """
    logging.debug('')#blank log just for the trace
    return_to = get_url_host(request) + reverse('user_complete_signin')
    return complete(request, return_to=return_to)

def signin_success(request, identity_url, openid_response):
    """
    this is not a view, has no url pointing to this

    this function is called when OpenID provider returns
    successful response to user authentication

    Does actual authentication in Django site and
    redirects to the registration page, if necessary
    or adds another login method.
    """

    logging.debug('')
    openid_data = util.from_openid_response(openid_response) #create janrain OpenID object
    request.session['openid'] = openid_data

    openid_url = str(openid_data)
    user = authenticate(
                    openid_url = openid_url,
                    method = 'openid'
                )

    next_url = get_next_url(request)
    provider_name = util.get_provider_name(openid_url)

    request.session['email'] = openid_data.sreg.get('email', '')
    request.session['username'] = openid_data.sreg.get('nickname', '')

    return finalize_generic_signin(
                        request = request,
                        user = user,
                        user_identifier = openid_url,
                        login_provider_name = provider_name
                    )

def finalize_generic_signin(
        request=None, user=None, login_provider_name=None, user_identifier=None,
    ):
    """non-view function
    generic signin, run after all protocol-dependent details
    have been resolved
    """
    redirect_url = request.session.pop('next_url', get_next_url(request))

    if 'in_recovery' in request.session:
        del request.session['in_recovery']
        redirect_url = getattr(django_settings, 'LOGIN_REDIRECT_URL', None)
        if redirect_url is None:
            redirect_url = reverse('questions')

    if request.user.is_authenticated():
        #this branch is for adding a new association
        if user is None:
            try:
                #see if currently logged in user has login with the given provider
                assoc = UserAssociation.objects.get(
                                    user=request.user,
                                    provider_name=login_provider_name
                                )
                logging.critical('switching account or open id changed???')
                #did openid url change? or we are dealing
                #with a brand new open id?
                #todo: populate
                #context = {
                #    'title': _('Login failed'),
                #    'message': _(
                #        'If you are trying to sign in to another account, '
                #        'please sign out first. '
                #        'Otherwise, please report the incident '
                #        'to the site administrator.'
                #    )
                #}
                #request.session['modal_menu']
                #context = {'title': _('OAuth login falied'), 'message': message}
                return HttpResponseRedirect(redirect_url)

            except UserAssociation.DoesNotExist:
                #register new association
                UserAssociation(
                    user=request.user,
                    provider_name=login_provider_name,
                    openid_url=user_identifier,
                    last_used_timestamp=datetime.datetime.now()
                ).save()
                close_modal_menu(request)
                return HttpResponseRedirect(redirect_url)

        elif user != request.user:
            #prevent theft of account by another pre-existing user
            logging.critical(
                    'possible account theft attempt by %s,%d to %s %d' % \
                    (
                        request.user.username,
                        request.user.id,
                        user.username,
                        user.id
                    )
                )
            logout(request)#log out current user
            login(request, user)#login freshly authenticated user
            close_modal_menu(request)
            return HttpResponseRedirect(redirect_url)
        else:
            #user just checks if another login still works
            #todo: populate request.session['modal_menu']
            #context = {
            #    'message': _('Your %(provider)s login works fine') % \
            #        {'provider': login_provider_name}
            #}
            return HttpResponseRedirect(redirect_url)
    elif user:
        #login branch
        login(request, user)
        logging.debug('login success')
        close_modal_menu(request)

        if askbot_settings.ASKBOT_CLOSED_FORUM_MODE:
            redirect_url = get_next_url(
                            request,
                            default=django_settings.LOGIN_REDIRECT_URL
                        )
        elif hasattr(user, '_askbot_new_post_url'):
                redirect_url = user._askbot_new_post_url

        return HttpResponseRedirect(redirect_url)
    else:
        assert(None not in (login_provider_name, user_identifier))
        request.session['login_provider_name'] = login_provider_name
        request.session['user_identifier'] = user_identifier
        if urlparse(redirect_url).path == reverse('user_signin'):
            #this branch is for signin in full-page version
            #here we need to redirect to the full-page verion
            #of the registration page
            data = get_register_form_context(request)
            close_modal_menu(request)
            return render(request, 'authopenid/complete_full.html', data)
        else:
            request.session['modal_menu'] = render_to_string(
                                    request,
                                    'authopenid/complete_modal.html',
                                    get_register_form_context(request)
                                )
        return HttpResponseRedirect(redirect_url)

def get_register_form_context(request):
    form_class = forms.get_registration_form_class()
    register_form = form_class(
        initial={
            'username': request.session.get('username', ''),
            'email': request.session.get('email', ''),
        }
    )
    return {
        'register_form': register_form,
        'modal_is_open': True
    }

@ajax_only
@post_only
@csrf.csrf_protect
@fix_recaptcha_remote_ip
def register(request, login_provider_name=None, user_identifier=None):
    """
    this function is used via it's own url with request.method=POST
    or as a simple function call from "finalize_generic_signin"
    in which case request.method must ge 'GET'
    and login_provider_name and user_identifier arguments must not be None

    user_identifier will be stored in the UserAssociation as openid_url
    login_provider_name - as provider_name

    this function may need to be refactored to simplify the usage pattern

    template : authopenid/complete.html
    """
    logging.debug('request method is %s' % request.method)

    assert(request.method == 'POST')

    if 'login_provider_name' not in request.session \
        or 'user_identifier' not in request.session:
        logging.critical('illegal attempt to register')
        return HttpResponseRedirect(get_next_url(request))

    #load this data from the session
    user_identifier = request.session['user_identifier']
    login_provider_name = request.session['login_provider_name']

    logging.debug('trying to create new account associated with openid')
    form_class = forms.get_registration_form_class()
    post_data = simplejson.loads(request.raw_post_data)
    register_form = form_class(post_data)

    if not register_form.is_valid():
        json_data = simplejson.dumps({'errors': register_form.errors, 'success': True})
        return HttpResponse(json_data, mimetype='application/json')
    else:
        username = register_form.cleaned_data['username']
        email = register_form.cleaned_data['email']

        if 'ldap_user_info' in request.session:
            user_info = request.session['ldap_user_info']
            #we take this info from the user input where
            #they can override the default provided by LDAP
            user_info['django_username'] = username
            user_info['email'] = email
            user = ldap_create_user(user_info).user
            user = authenticate(user_id=user.id, method='force')
            del request.session['ldap_user_info']
            login(request, user)
            cleanup_post_register_session(request)
            close_modal_menu(request)

        elif askbot_settings.REQUIRE_VALID_EMAIL_FOR == 'nothing':

            user = create_authenticated_user_account(
                        username=username,
                        email=email,
                        user_identifier=user_identifier,
                        login_provider_name=login_provider_name,
                    )
            login(request, user)
            cleanup_post_register_session(request)
            close_modal_menu(request)
        else:
            #todo: broken branch
            raise NotImplementedError()
            request.session['username'] = username
            request.session['email'] = email
            key = generate_random_key()
            email = request.session['email']
            send_email_key(email, key, handler_url_name='verify_email_and_register')
            request.session['validation_code'] = key
            redirect_url = reverse('verify_email_and_register') \
                            + '?next=' + get_next_url(request)
            close_modal_menu(request)
            raise NotImplementedError()
            return HttpResponseRedirect(redirect_url)

        return render_to_json_response(get_logged_in_user_data(request, user))

    raise NotImplementedError('should never fall through here')

def signin_failure(request, message):
    """
    falure with openid signin. Go back to signin page.
    """
    request.user.message_set.create(message = message)
    return HttpResponseRedirect(get_next_url(request))

@not_authenticated
@csrf.csrf_protect
def verify_email_and_register(request):
    """for POST request - check the validation code,
    and if correct - create an account an log in the user

    for GET - give a field to paste the activation code
    and a button to send another validation email.
    """
    presented_code = request.REQUEST.get('validation_code', None)
    if presented_code:
        try:
            #we get here with post if button is pushed
            #or with "get" if emailed link is clicked
            email_verifier = UserEmailVerifier.objects.get(key=presented_code)
            #verifies that the code has not been used already
            assert(email_verifier.verified == False)
            assert(email_verifier.has_expired() == False)

            username = email_verifier.value['username']
            email = email_verifier.value['email']
            password = email_verifier.value.get('password', None)
            user_identifier = email_verifier.value.get('user_identifier', None)
            login_provider_name = email_verifier.value.get('login_provider_name', None)

            if password:
                user = create_authenticated_user_account(
                    username=username,
                    email=email,
                    password=password,
                )
            elif user_identifier and login_provider_name:
                user = create_authenticated_user_account(
                    username=username,
                    email=email,
                    user_identifier=user_identifier,
                    login_provider_name=login_provider_name,
                )
            else:
                raise NotImplementedError()

            login(request, user)
            email_verifier.verified = True
            email_verifier.save()
            cleanup_post_register_session(request)

            return HttpResponseRedirect(get_next_url(request))
        except Exception, e:
            message = _(
                'Sorry, registration failed. '
                'The token can be already used or has expired. Please try again'
            )
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(reverse('index'))
    else:
        data = {'page_class': 'validate-email-page'}
        return render(request, 'authopenid/verify_email.html', data)

@csrf.csrf_protect
@ajax_only
@post_only
def register_with_password(request):
    """Create a password-protected account
    template: authopenid/signup_with_password.html
    """
    post_data = simplejson.loads(request.raw_post_data)
    form = forms.ClassicRegisterForm(post_data)

    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        email = form.cleaned_data['email']

        if askbot_settings.REQUIRE_VALID_EMAIL_FOR == 'nothing':
            user = create_authenticated_user_account(
                username=username,
                email=email,
                password=password,
            )
            login(request, user)
            cleanup_post_register_session(request)
            #get user tools nav login snippet
            return get_logged_in_user_data(request, user)
        else:
            request.session['username'] = username
            request.session['email'] = email
            request.session['password'] = password
            #todo: generate a key and save it in the session
            key = generate_random_key()
            email = request.session['email']
            send_email_key(email, key, handler_url_name='verify_email_and_register')
            request.session['validation_code'] = key
            redirect_url = reverse('verify_email_and_register') + \
                            '?next=' + get_next_url(request)
            return HttpResponseRedirect(redirect_url)
    else:
        #todo return data via ajax
        return {'errors': form.errors}

@csrf.csrf_protect
@ajax_only
def ajax_signout(request):
    """sign out view specifically for the ajax use"""
    if request.user.is_anonymous():
        raise django_exceptions.PermissionDenied()
    logout(request)
    userToolsHtml = render_to_string(request, 'widgets/user_navigation.html')
    loginMenuHtml = render_to_string(
                        request,
                        'authopenid/signin_modal.html',
                        get_signin_view_context(request)
                    )
    return {
        'userToolsNavHtml': userToolsHtml,
        'loginMenuHtml': loginMenuHtml
    }

@csrf.csrf_protect
@ajax_only
def get_login_menu_html(request):
    loginMenuHtml = render_to_string(
                        request,
                        'authopenid/signin_modal.html',
                        get_signin_view_context(request)
                    )
    return {'loginMenuHtml': loginMenuHtml}

@login_required
def signout(request):
    """signout from the website. Remove openid from session and kill it.
    url : /signout/"""
    logout(request)
    logging.debug('user logged out')
    return HttpResponseRedirect(get_next_url(request))


XRDF_TEMPLATE = """<?xml version='1.0' encoding='UTF-8'?>
<xrds:XRDS
   xmlns:xrds='xri://$xrds'
   xmlns:openid='http://openid.net/xmlns/1.0'
   xmlns='xri://$xrd*($v*2.0)'>
 <XRD>
   <Service>
     <Type>http://specs.openid.net/auth/2.0/return_to</Type>
     <URI>%(return_to)s</URI>
   </Service>
 </XRD>
</xrds:XRDS>"""

def xrdf(request):
    url_host = get_url_host(request)
    return_to = "%s%s" % (url_host, reverse('user_complete_signin'))
    return HttpResponse(XRDF_TEMPLATE % {'return_to': return_to})

def set_new_email(user, new_email):
    if new_email != user.email:
        user.email = new_email
        user.email_isvalid = False
        user.save()

def send_user_new_email_key(user):
    user.email_key = generate_random_key()
    user.save()
    send_email_key(user.email, user.email_key)

@csrf.csrf_protect
def account_recover(request):
    """view similar to send_email_key, except
    it allows user to recover an account by entering
    his/her email address

    this view will both - send the recover link and
    process it

    url name 'user_account_recover'
    """
    if not askbot_settings.ALLOW_ACCOUNT_RECOVERY_BY_EMAIL:
        raise Http404
    if request.method == 'POST':
        post_data = simplejson.loads(request.raw_post_data)
        form = forms.AccountRecoveryForm(post_data)
        if form.is_valid():
            user = form.cleaned_data['user']
            send_user_new_email_key(user)
            response = simplejson.dumps({'success': True})
        else:
            response = simplejson.dumps({'errors': form.errors, 'success': True})
        return HttpResponse(response, mimetype='application/json')
    else:
        key = request.GET.get('validation_code', None)
        if key is None:
            message = _(
                'Hmm, could not recover your account - maybe '
                'the validation link was incorrect?'
            )
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(get_next_url(request))

        user = authenticate(email_key=key, method='email')
        if user:
            if request.user.is_authenticated():
                if user != request.user:
                    logout(request)
                    login(request, user)
            else:
                login(request, user)

            from askbot.models import greet_new_user
            greet_new_user(user)

            #need to show "sticky" signin view here
            request.session['in_recovery'] = True
            #open blocking modal account recovery menu
            request.session['modal_menu'] = render_to_string(
                                    request,
                                    'authopenid/establish_login_modal.html',
                                    get_establish_login_view_context(request)
                                )
            from askbot.search.state_manager import SearchState
            return HttpResponseRedirect(SearchState().base_url())
        else:
            message = _('Recovery link was invalid, please try again')
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(get_next_url(request))


def get_establish_login_view_context(request):
    """prepares context for the establish login menu"""
    next_url = get_next_url(request)
    login_form = forms.LoginForm(
                    initial={'next': next_url},
                    prefix='login'
                )
    data = {
        'login_form': login_form,
        'set_password_form': forms.SetPasswordForm(prefix='set_password'),
        'use_password_login': util.use_password_login(),
        'modal_is_open': True
    }

    login_providers = util.get_enabled_login_providers()
    data['login_providers'] = login_providers.values()

    #determine if we are only using password login or we also have buttons
    active_provider_names = [p['name'] for p in login_providers.values()]
    data['have_buttons'] = len(active_provider_names)

    #todo: add user's active login methods for the users to see and 
    #delete if they want to
        
    data.update(csrf_context(request))
    return data
