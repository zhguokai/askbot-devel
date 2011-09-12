"""extra context data for the registration
pages"""
from django.core.urlresolvers import reverse
from django_authenticator import util
from django_authenticator import forms

PASSWORD_REGISTRATION_CONTEXT = {
    'login_form': forms.LoginForm(),
    'major_login_providers': util.get_enabled_major_login_providers().values(),
    'minor_login_providers': util.get_enabled_minor_login_providers().values(),
}
