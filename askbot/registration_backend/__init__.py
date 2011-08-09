"""default registration backend for askbot

Use of this backend requires a session variable:
``registration_type``, that can take one of the values:
* 'without-password' - for federated auth systems
* 'with-password' - traditional password
* 'with-password-and-recaptcha' - ... + recaptcha

After registration is completed, the session variable is deleted
"""
import datetime
import logging
from django.http import Http404
from django.core.urlresolvers import resolve, reverse
from django.contrib.auth.models import User
from registration.models import RegistrationProfile
from registration import signals
from askbot.conf import settings as askbot_settings
from askbot import forms
from askbot.utils.forms import get_next_url

def redirect_to_next_url(self, request, user):
    next_url = get_next_url(request)
    try:
        return resolve(next_url)
    except Http404:
        return ('index', None, None)


class RegistrationBackend(object):
    """The registration backend class for askbot,
    to be used with the application ``django-registration``.

    This backend supports traditional registration with 
    password, as well as registrations through third party login
    providers of various types
    """

    def register(self, request, **form_data):
        """Creates user account"""
        username = form_data['username']
        email = form_data['email']
        #we rely on these two values to finish registration
        #in the user_registered signal handler
        #here, depending on the registration type, we might 
        user = User.objects.create_user(username, email = email)
        if request.path == reverse('registration_register_with_password'):
            user.set_password(form_data['new_password1'])
            user.save()
            #unlike in the federated logins, in this case
            #there is no intermediary view which sets these 
            #session valriables. We need them in order to
            #create user associacion with the login method.
            request.session['login_provider_name'] = 'local'
            request.session['user_identifier'] = '%s@local' % username
        elif request.path == reverse('registration_register'):
            #for any registration that does not create local 
            #password - we need to make sure that they were
            #initiated from the login system working with askbot
            #not the handcrafted query
            assert('login_provider_name' in request.session)
            assert('user_identifier' in request.session)
        else:
            raise NotImplementedError('Invalid registration url was used')

        #todo: this can be called via a dedicated method
        #allowing to save extra data, that might be required
        #for the customized site
        subscribe_form = forms.SimpleEmailSubscribeForm(form_data)
        subscribe_form.full_clean()
        subscribe_form.save(user = user)
        
        #create the user here!
        signals.user_registered.send(
            sender = RegistrationBackend,
            request = request,
            user = user
        )

    def activate(self, request, **kwargs):
        if askbot_settings.EMAIL_VALIDATION == False:
            raise NotImplementedError()
        try:
            key = kwargs.get('activation_key', None)
            profile = RegistrationProfile.objects.get(activation_key = key)
        except RegistrationProfile.DoesNotExist:
            return False

        profile.user.is_active = True
        profile.user.save()
        return profile.user

    def registration_allowed(self, request):
        #todo - may add an optional condition say require
        #invitation to register
        if request.path == reverse('registration_register_with_password'):
            #no need to check authenticity of request when registering
            #user with locally stored password
            return True
        token = request.session.get('authenticator_registration_token', None)
        if token is None:
            return False
        else:
            new_addr = request.META['REMOTE_ADDR']
            new_time = datetime.datetime.now()
            old_addr = token['remote_addr']
            old_time = token['timestamp']
            if new_addr == old_addr:
                if new_time > old_time:
                    #give 10 minutes, then timeout
                    if new_time - old_time <= datetime.timedelta(0, 600):
                        return True
        return False

    def get_form_class(self, request):
        """returns class of the user registration
        form, depending on the url that was hit
        and whether recaptcha is enabled"""
        if request.path == reverse('registration_register'):
            return forms.OpenidRegisterForm
        elif request.path == reverse('registration_register_with_password'):
            if askbot_settings.USE_RECAPTCHA:
                return forms.SafeClassicRegisterForm
            else:
                return forms.ClassicRegisterForm
        else:
            raise NotImplementedError('invalid url was used for the registration page')

    post_registration_redirect = redirect_to_next_url
    post_activation_redirect = redirect_to_next_url
