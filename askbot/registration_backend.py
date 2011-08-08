"""default registration backend for askbot

Use of this backend requires a session variable:
``registration_type``, that can take one of the values:
* 'without-password' - for federated auth systems
* 'with-password' - traditional password
* 'with-password-and-recaptcha' - ... + recaptcha

After registration is completed, the session variable is deleted
"""
import logging
from django.http import Http404
from django.core.urlresolvers import resolve
from django.contrib.auth.models import User
from registration.models import RegistrationProfile
from registration import signals
from askbot.conf import settings as askbot_settings
from askbot import forms
from askbot.utils.forms import get_next_url

def redirect_to_next_url(self, request, user):
    next_url = get_next_url(request)
    try:
        match = resolve(next_url)
        return (match.url_name, match.args, match.kwargs)
    except Http404:
        return ('index', None, None)


class RegistrationBackend(object):
    """The registration backend class for askbot,
    to be used with the application ``django-registration``.
    """

    def register(self, request, **form_data):
        """Creates user account"""
        username = form_data['username']
        email = form_data['email']
        #we rely on these two values to finish registration
        #in the user_registered signal handler
        #here, depending on the registration type, we might 
        user = User.objects.create_user(username, email = email)
        if form_data['reg_type'].startswith('with-password'):
            user.set_password(form_data['new_password1'])
            user.save()
        else:
            #for any registration that does not create local 
            #password - we need to make sure that they were
            #initiated from the login system working with askbot
            #not the handcrafted query
            assert('login_provider_name' in request.session)
            assert('user_identifier' in request.session)

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
        return True

    def get_form_class(self, request):
        reg_type = request.session.get('registration_type', None)
        if reg_type == 'passwordless':
            return forms.OpenidRegisterForm
        elif reg_type == 'with-password':
            return forms.ClassicRegisterForm
        elif reg_type == 'with-password-and-recaptcha':
            return forms.SafeClassicRegisterForm
        else:
            logging.error('session variable "regisration_type" must be set')
            raise NotImplementedError()

    post_registration_redirect = redirect_to_next_url
    post_activation_redirect = redirect_to_next_url
