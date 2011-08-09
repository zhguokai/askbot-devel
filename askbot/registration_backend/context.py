"""extra context data for the registration
pages"""
from django.core.urlresolvers import reverse
from askbot.deps.django_authopenid import util
from askbot.deps.django_authopenid import forms

PASSWORD_REGISTRATION_CONTEXT = {
    'login_form': forms.LoginForm(),
    'major_login_providers': util.get_enabled_major_login_providers().values(),
    'minor_login_providers': util.get_enabled_minor_login_providers().values(),
}
