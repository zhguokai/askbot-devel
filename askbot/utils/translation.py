from django.conf import settings as django_settings
from askbot.conf import settings as askbot_settings
from django.utils import translation

def get_language():
    if getattr(django_settings, 'ASKBOT_MULTILINGUAL', False):
        return translation.get_language()
    else:
        return askbot_settings.ASKBOT_LANGUAGE
