"""authentication backend that takes care of the
multiple login methods supported by the authenticator
application
"""
import datetime
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend as AuthModelBackend
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _
from askbot.deps.django_authopenid.models import UserAssociation
from askbot.deps.django_authopenid import util

def authenticate_by_association(identifier = None, provider_name = None):
    """returns user stored in the matching instance of the
    user association

    Format of identifier is described in the doc string of
    :meth:`AuthBackend.authenticate`
    """
    try:
        assoc = UserAssociation.objects.get(
                        openid_url = identifier,#parameter name is bad
                        provider_name = provider_name
                    )
        assoc.last_used_timestamp = datetime.datetime.now()
        assoc.save()
        return assoc.user
    except UserAssociation.DoesNotExist:
        return None

THIRD_PARTY_PROVIDER_TYPES = (
    'openid', 'password' 'oauth', 'ldap', 'facebook',
    'password-external'
)

class AuthBackend(object):
    """Authenticator's authentication backend class
    for more info, see django doc page:
    http://docs.djangoproject.com/en/dev/topics/auth/#writing-an-authentication-backend

    the reason there is only one class - for simplicity of
    adding this application to a django project - users only need
    to extend the AUTHENTICATION_BACKENDS with a single line
    """

    def authenticate(
                self,
                identifier = None,# -
                username = None,#for 'password'
                password = None,#for 'password'
                provider_name = None,#required with all except email_key
                method = None,#requried parameter
            ):
        """this authentication function supports many login methods
        just which method it is going to use it determined
        by the value of ``method``

        returns a user object or ``None``

        Format for the ``identifier`` by type of authentication provider:

        * openid - openid url as is
        * password - username@local - for local pw based login
        * password-external - username@provider_name - for external pw login provider
        * facebook - facebook_user_id
        * oauth - oauth_provider_user id in the form of string
        * ldap - user id in the ldap system

        In all cases - the identifier parameter is a string.
        """
        if method == 'password':
            #reuse standard backend from django.contrib.auth
            backend = AuthModelBackend()
            return backend.authenticate(username, password)
        elif method == 'password-external':
            login_providers = util.get_enabled_login_providers()
            check_pw_func = login_providers[provider_name]['check_password']
            if check_pw_func(username, password):
                user, created = get_or_create_unique_user(
                    preferred_username = username,
                    login_provider_name = provider_name
                )
                return user, created
            else:
                return None
        elif method in THIRD_PARTY_PROVIDER_TYPES:
            #any third party logins. here we guarantee that
            #user already passed external authentication
            return authenticate_by_association(
                identifier = identifier,
                provider_name = provider_name
            )
        elif method == 'email':
            try:
                #todo: add email_key_timestamp field
                #and check key age
                user = User.objects.get(email_key = identifier)
                user.email_key = None #one time key so delete it
                user.email_isvalid = True
                user.save()
                return user
            except User.DoesNotExist:
                return None
        elif method == 'force':
            return self.get_user(identifier)
        else:
            raise NotImplementedError('unknown provider type %s' % method)

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @classmethod
    def set_password(cls, 
                    user=None,
                    password=None,
                    provider_name=None
                ):
        """generic method to change password of
        any for any login provider that uses password
        and allows the password change function
        """
        login_providers = util.get_enabled_login_providers()
        if login_providers[provider_name]['type'] != 'password':
            raise ImproperlyConfigured('login provider must use password')

        if provider_name == 'local':
            user.set_password(password)
            user.save()
            scrambled_password = user.password + str(user.id)
        else:
            raise NotImplementedError('external passwords not supported')

        try:
            assoc = UserAssociation.objects.get(
                                        user = user,
                                        provider_name = provider_name
                                    )
        except UserAssociation.DoesNotExist:
            assoc = UserAssociation(
                        user = user,
                        provider_name = provider_name
                    )

        assoc.openid_url = scrambled_password
        assoc.last_used_timestamp = datetime.datetime.now()
        assoc.save()
