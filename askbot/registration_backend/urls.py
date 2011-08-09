"""mostly copy-paste from the default registration backend
taken from :mod:`registration.backends.default.urls`

The customized parts are - translated urls and
attached the askbot's registration backend instead of
the default backend

Besides django-registration, this backend needs app
askbot.deps.django_authopenid authentication app
"""
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext as _

from registration.views import activate
from registration.views import register
from askbot.registration_backend import context

REGISTRATION_BACKEND = 'askbot.registration_backend.RegistrationBackend'
urlpatterns = patterns('',
    url(
        r'^%s%s$' % (_('activate/'), _('complete/')),
        direct_to_template,
        {'template': 'registration/activation_complete.html'},
        name = 'registration_activation_complete'
    ),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(
        r'^%s/(?P<activation_key>\w+)/$' % _('activate/'),
        activate,
        {'backend': REGISTRATION_BACKEND},
        name='registration_activate'
    ),
    url(
        r'^%s$' % _('with-password/'),
        register,
        kwargs = {
            'backend': REGISTRATION_BACKEND,
            'extra_context': context.PASSWORD_REGISTRATION_CONTEXT,
            'template_name': 'registration/password_registration_form.html'
        },
        name='registration_register_with_password'
    ),
    url(
        r'^%s$' % _('through-other-site/'),
        register,
        kwargs = {
            'backend': REGISTRATION_BACKEND,
            'template_name': 'registration/external_registration_form.html'
        },
        name='registration_register'
    ),
    url(
        r'^%s%s$' % (_('register/'), _('complete/')),
        direct_to_template,
        {'template': 'registration/registration_complete.html'},
        name='registration_complete'
    ),
    url(
        r'^%s%s$' % (_('register/'), _('closed/')),
        direct_to_template,
        {'template': 'registration/registration_closed.html'},
        name='registration_disallowed'
    ),
    #(r'', include('registration.auth_urls')),
)
