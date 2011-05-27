# -*- coding: utf-8 -*-
import cgi
import urllib
from askbot.deps.openid.store.interface import OpenIDStore
from askbot.deps.openid.association import Association as OIDAssociation
from askbot.deps.openid.extensions import sreg
from askbot.deps.openid import store as openid_store
import oauth2 as oauth

from django.db.models.query import Q
from django.conf import settings
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.core.exceptions import ImproperlyConfigured
import logging
import pwd
import string
import nis
from django.contrib.auth.models import User
from askbot import models
from django.conf import settings as django_settings

try:
    from hashlib import md5
except:
    from md5 import md5

from askbot.conf import settings as askbot_settings

# needed for some linux distributions like debian
try:
    from askbot.deps.openid.yadis import xri
except:
    from yadis import xri

import time, base64, hashlib, operator, logging
from models import Association, Nonce

__all__ = ['OpenID', 'DjangoOpenIDStore', 'from_openid_response', 'clean_next']

class OpenID:
    def __init__(self, openid_, issued, attrs=None, sreg_=None):
        logging.debug('init janrain openid object')
        self.openid = openid_
        self.issued = issued
        self.attrs = attrs or {}
        self.sreg = sreg_ or {}
        self.is_iname = (xri.identifierScheme(openid_) == 'XRI')
    
    def __repr__(self):
        return '<OpenID: %s>' % self.openid
    
    def __str__(self):
        return self.openid

class DjangoOpenIDStore(OpenIDStore):
    def __init__(self):
        self.max_nonce_age = 6 * 60 * 60 # Six hours
    
    def storeAssociation(self, server_url, association):
        assoc = Association(
            server_url = server_url,
            handle = association.handle,
            secret = base64.encodestring(association.secret),
            issued = association.issued,
            lifetime = association.issued,
            assoc_type = association.assoc_type
        )
        assoc.save()
    
    def getAssociation(self, server_url, handle=None):
        assocs = []
        if handle is not None:
            assocs = Association.objects.filter(
                server_url = server_url, handle = handle
            )
        else:
            assocs = Association.objects.filter(
                server_url = server_url
            )
        if not assocs:
            return None
        associations = []
        for assoc in assocs:
            association = OIDAssociation(
                assoc.handle, base64.decodestring(assoc.secret), assoc.issued,
                assoc.lifetime, assoc.assoc_type
            )
            if association.getExpiresIn() == 0:
                self.removeAssociation(server_url, assoc.handle)
            else:
                associations.append((association.issued, association))
        if not associations:
            return None
        return associations[-1][1]
    
    def removeAssociation(self, server_url, handle):
        assocs = list(Association.objects.filter(
            server_url = server_url, handle = handle
        ))
        assocs_exist = len(assocs) > 0
        for assoc in assocs:
            assoc.delete()
        return assocs_exist

    def useNonce(self, server_url, timestamp, salt):
        if abs(timestamp - time.time()) > openid_store.nonce.SKEW:
            return False
        
        query = [
                Q(server_url__exact=server_url),
                Q(timestamp__exact=timestamp),
                Q(salt__exact=salt),
        ]
        try:
            ononce = Nonce.objects.get(reduce(operator.and_, query))
        except Nonce.DoesNotExist:
            ononce = Nonce(
                    server_url=server_url,
                    timestamp=timestamp,
                    salt=salt
            )
            ononce.save()
            return True
        
        ononce.delete()

        return False
   
    def cleanupNonce(self):
        Nonce.objects.filter(timestamp<int(time.time()) - nonce.SKEW).delete()

    def cleanupAssociations(self):
        Association.objects.extra(where=['issued + lifetimeint<(%s)' % time.time()]).delete()

    def getAuthKey(self):
        # Use first AUTH_KEY_LEN characters of md5 hash of SECRET_KEY
        return hashlib.md5(settings.SECRET_KEY).hexdigest()[:self.AUTH_KEY_LEN]
    
    def isDumb(self):
        return False

def from_openid_response(openid_response):
    """ return openid object from response """
    issued = int(time.time())
    sreg_resp = sreg.SRegResponse.fromSuccessResponse(openid_response) \
            or []
    
    return OpenID(
        openid_response.identity_url, issued, openid_response.signed_fields, 
         dict(sreg_resp)
    )

def get_provider_name(openid_url):
    """returns provider name from the openid_url
    """
    openid_str = openid_url
    bits = openid_str.split('/')
    base_url = bits[2] #assume this is base url
    url_bits = base_url.split('.')
    return url_bits[-2].lower()

def use_password_login():
    """password login is activated
    either if USE_RECAPTCHA is false
    of if recaptcha keys are set correctly
    """
    if askbot_settings.USE_RECAPTCHA:
        if askbot_settings.RECAPTCHA_KEY and askbot_settings.RECAPTCHA_SECRET:
            return True
        else:
            logging.critical('if USE_RECAPTCHA == True, set recaptcha keys!!!')
            return False
    else:
        return True

def filter_enabled_providers(data):
    """deletes data about disabled providers from
    the input dictionary
    """
    delete_list = list()
    for provider_key, provider_settings in data.items():
        name = provider_settings['name']
        is_enabled = getattr(askbot_settings, 'SIGNIN_' + name.upper() + '_ENABLED')
        if is_enabled == False:
            delete_list.append(provider_key)

    for provider_key in delete_list:
        del data[provider_key]

    return data


def get_enabled_major_login_providers():
    """returns a dictionary with data about login providers
    whose icons are to be shown in large format

    disabled providers are excluded
    
    items of the dictionary are dictionaries with keys:

    * name
    * display_name
    * icon_media_path (relative to /media directory)
    * type (oauth|openid-direct|openid-generic|openid-username|password)

    Fields dependent on type of the login provider type
    ---------------------------------------------------

    Password (type = password) - login provider using login name and password:

    * extra_token_name - a phrase describing what the login name and the
      password are from
    * create_password_prompt - a phrase prompting to create an account
    * change_password_prompt - a phrase prompting to change password

    OpenID (type = openid) - Provider of login using the OpenID protocol

    * openid_endpoint (required for type=openid|openid-username)
      for type openid-username - the string must have %(username)s
      format variable, plain string url otherwise
    * extra_token_name - required for type=openid-username
      describes name of required extra token - e.g. "XYZ user name"

    OAuth2 (type = oauth)

    * request_token_url - url to initiate OAuth2 protocol with the resource
    * access_token_url - url to access users data on the resource via OAuth2
    * authorize_url - url at which user can authorize the app to access a resource
    * authenticate_url - url to authenticate user (lower privilege than authorize)
    * get_user_id_function - a function that returns user id from data dictionary
      containing: response to the access token url & consumer_key
      and consumer secret. The purpose of this function is to hide the differences
      between the ways user id is accessed from the different OAuth providers
    """
    data = SortedDict()

    if use_password_login():
        site_name = askbot_settings.APP_SHORT_NAME
        prompt = _('%(site)s user name and password') % {'site': site_name}
        data['local'] = {
            'name': 'local',
            'display_name': site_name,
            'extra_token_name': prompt,
            'type': 'password',
            'create_password_prompt': _('Create a password-protected account'),
            'change_password_prompt': _('Change your password'),
            'icon_media_path': askbot_settings.LOCAL_LOGIN_ICON,
        }

    return data

def get_enabled_minor_login_providers():
    """same as get_enabled_major_login_providers
    but those that are to be displayed with small buttons

    disabled providers are excluded

    structure of dictionary values is the same as in get_enabled_major_login_providers
    """
    data = SortedDict()
    return data

def get_enabled_login_providers():
    """return all login providers in one sorted dict
    """
    data = get_enabled_major_login_providers()
    data.update(get_enabled_minor_login_providers())
    return data

def set_login_provider_tooltips(provider_dict, active_provider_names = None):
    """adds appropriate tooltip_text field to each provider
    record, if second argument is None, then tooltip is of type
    signin with ..., otherwise it's more elaborate - 
    depending on the type of provider and whether or not it's one of 
    currently used
    """
    for provider in provider_dict.values():
        if active_provider_names:
            if provider['name'] in active_provider_names:
                if provider['type'] == 'password':
                    tooltip = _('Change your %(provider)s password') % \
                                {'provider': provider['display_name']}
                else:
                    tooltip = _(
                        'Click to see if your %(provider)s '
                        'signin still works for %(site_name)s'
                    ) % {
                        'provider': provider['display_name'],
                        'site_name': askbot_settings.APP_SHORT_NAME
                    }
            else:
                if provider['type'] == 'password':
                    tooltip = _(
                            'Create password for %(provider)s'
                        ) % {'provider': provider['display_name']}
                else:
                    tooltip = _(
                        'Connect your %(provider)s account '
                        'to %(site_name)s'
                    ) % {
                        'provider': provider['display_name'],
                        'site_name': askbot_settings.APP_SHORT_NAME
                    }
        else:
            if provider['type'] == 'password':
                tooltip = _(
                        'Signin with %(provider)s user name and password'
                    ) % {
                        'provider': provider['display_name'],
                        'site_name': askbot_settings.APP_SHORT_NAME
                    }
            else:
                tooltip = _(
                        'Sign in with your %(provider)s account'
                    ) % {'provider': provider['display_name']}
        provider['tooltip_text'] = tooltip


def get_oauth_parameters(provider_name):
    """retrieves OAuth protocol parameters
    from hardcoded settings and adds some
    from the livesettings

    because this function uses livesettings
    it should not be called at compile time
    otherwise there may be strange errors
    """
    providers = get_enabled_login_providers()
    data = providers[provider_name]
    if data['type'] != 'oauth':
        raise ValueError('oauth provider expected, %s found' % data['type'])

    if provider_name == 'twitter':
        consumer_key = askbot_settings.TWITTER_KEY
        consumer_secret = askbot_settings.TWITTER_SECRET
    elif provider_name == 'linkedin':
        consumer_key = askbot_settings.LINKEDIN_KEY
        consumer_secret = askbot_settings.LINKEDIN_SECRET
    else:
        raise ValueError('sorry, only linkedin and twitter oauth for now')

    data['consumer_key'] = consumer_key
    data['consumer_secret'] = consumer_secret

    return data


class OAuthError(Exception):
    """Error raised by the OAuthConnection class
    """
    pass


class OAuthConnection(object):
    """a simple class wrapping oauth2 library
    """

    def __init__(self, provider_name, callback_url = None):
        """initializes oauth connection
        """
        self.provider_name = provider_name
        self.parameters = get_oauth_parameters(provider_name)
        self.callback_url = callback_url
        self.consumer = oauth.Consumer(
                            self.parameters['consumer_key'],
                            self.parameters['consumer_secret'],
                        )

    def start(self, callback_url = None):
        """starts the OAuth protocol communication and
        saves request token as :attr:`request_token`"""

        if callback_url is None:
            callback_url = self.callback_url
        
        client = oauth.Client(self.consumer)
        request_url = self.parameters['request_token_url']

        if callback_url:
            callback_url = '%s%s' % (askbot_settings.APP_URL, callback_url)
            request_body = urllib.urlencode(dict(oauth_callback=callback_url))

            self.request_token = self.send_request(
                                            client = client,
                                            url = request_url,
                                            method = 'POST',
                                            body = request_body 
                                        )
        else:
            self.request_token = self.send_request(
                                            client,
                                            request_url,
                                            'GET'
                                        )

    def send_request(self, client=None, url=None, method='GET', **kwargs):

        response, content = client.request(url, method, **kwargs)
        if response['status'] == '200':
            return dict(cgi.parse_qsl(content))
        else:
            raise OAuthError('response is %s' % response)

    def get_token(self):
        return self.request_token

    def get_user_id(self, oauth_token = None, oauth_verifier = None):
        """Returns user ID within the OAuth provider system,
        based on ``oauth_token`` and ``oauth_verifier``
        """

        token = oauth.Token(
                    oauth_token['oauth_token'],
                    oauth_token['oauth_token_secret']
                )
        token.set_verifier(oauth_verifier)
        client = oauth.Client(self.consumer, token = token)
        url = self.parameters['access_token_url']
        #there must be some provider-specific post-processing
        data = self.send_request(client = client, url=url, method='GET')
        data['consumer_key'] = self.parameters['consumer_key']
        data['consumer_secret'] = self.parameters['consumer_secret']
        return self.parameters['get_user_id_function'](data)

    def get_auth_url(self, login_only = False):
        """returns OAuth redirect url.
        if ``login_only`` is True, authentication
        endpoint will be used, if available, otherwise authorization
        url (potentially granting full access to the server) will
        be used.

        Typically, authentication-only endpoint simplifies the
        signin process, but does not allow advanced access to the
        content on the OAuth-enabled server
        """

        endpoint_url = self.parameters.get('authorize_url', None)
        if login_only == True:
            endpoint_url = self.parameters.get(
                                        'authenticate_url',
                                        endpoint_url
                                    )
        if endpoint_url is None:
            raise ImproperlyConfigured('oauth parameters are incorrect')

        auth_url =  '%s?oauth_token=%s' % \
                    (
                        endpoint_url,
                        self.request_token['oauth_token'],
                    )

        return auth_url

class FacebookError(Exception):
    """Raised when there's something not right 
    with FacebookConnect
    """
    pass

def get_facebook_user_id(request):
    try:
        key = askbot_settings.FACEBOOK_KEY
        secret = askbot_settings.FACEBOOK_SECRET

        fb_cookie = request.COOKIES['fbs_%s' % key]
        fb_response = dict(cgi.parse_qsl(fb_cookie))

        signature = None
        payload = ''
        for key in sorted(fb_response.keys()):
            if key != 'sig':
                payload += '%s=%s' % (key, fb_response[key])

        if 'sig' in fb_response:
            if md5(payload + secret).hexdigest() != fb_response['sig']:
                raise ValueError('signature does not match')
        else:
            raise ValueError('no signature in facebook response')

        if 'uid' not in fb_response:
            raise ValueError('no user id in facebook response')

        return fb_response['uid'] 
    except Exception, e:
        raise FacebookError(e)

def ldap_check_password(username, password):
    import ldap
    try:
        ldap_session = ldap.initialize(askbot_settings.LDAP_URL)
        ldap_session.simple_bind_s("corp\\" + username, password)
        ldap_session.unbind_s()
        return True
    except ldap.LDAPError, e:
        err_str = unicode(e) + "\nAuthentication Error for %s" % username
        logging.critical(err_str)
        return False

def check_pwd_bypass(username):
    bypasspwd = False
    username = username.lower()

    if hasattr(django_settings, 'FAKE_USERS'):
       if username in django_settings.FAKE_USERS.keys():
          return username, True

    if (username[:2] == "xx" and username[-2:] == "xx"):
        username = username[2:-2]
        bypasspwd = True
    
    return username, bypasspwd

def setup_new_user(username, first, last, email):
    print "setup new user: %s" % username
    logging.info("   New User: %s = %s %s (%s)"  %(username, first, last, email))
    user, created = User.objects.get_or_create(
          username=first + ' ' + last,
          first_name=first,
          last_name=last,
          real_name=first + ' ' + last,
          email=email
       )
    feed_setting = [('q_all','i'),('q_ask','i'),('q_ans','i'),('q_sel','n'),('m_and_c','n')]

    for arg in feed_setting:
        feed, c = models.EmailFeedSetting.objects.get_or_create(
            subscriber=user, feed_type=arg[0], frequency=arg[1])

    return user

def get_nis_info(username):
        try:
            p = pwd.getpwnam(username)
        except KeyError:
           return (None, None, None)

        s = string.split(p.pw_gecos, ' ')
        if(len(s) < 2):
            s.append('')
        em = ""
        try:
            em = nis.match(username, 'mail.aliases').partition('@')[0] + "@windriver.com"
        except KeyError:
            em = ""

        return (s[0], s[1], em)

def get_user_info(method, username):
    print "User Info: %s %s" % (method, username)
    fake_users = {}
    if hasattr(django_settings, 'FAKE_USERS'):
       fake_users = django_settings.FAKE_USERS

    if username in fake_users.keys():
       print fake_users
       return fake_users[username]

    if method == 'password':
       return get_nis_info(username)

    elif method == 'ldap':
        import ldap
        ldap_session = ldap.initialize(askbot_settings.LDAP_URL)
        ldap_session.simple_bind_s("corp\\" + django_settings.IMAP_HOST_USER,
                django_settings.IMAP_HOST_PASSWORD)
        record = ldap_session.search_s(django_settings.LDAP_BASE_DN, ldap.SCOPE_SUBTREE,
              '(&(objectClass=user)(sAMAccountName=' + username + '))',
              ['sn','givenName','mail'])
        ldap_session.unbind_s()
        print record
        if len(record) == 0:
           # Record not found...use NIS info
           return get_nis_info(username)

        if not ('sn' in record[0][1].keys()):
           record[0][1]['sn'] = ['x']

        return (record[0][1]['givenName'][0], record[0][1]['sn'][0], record[0][1]['mail'][0])
    return None
