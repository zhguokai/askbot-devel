"""functions for managing Q&A spaces"""
from django.conf import settings as django_settings
from django.utils.translation import ugettext as _
from askbot.conf import settings as askbot_settings

def get_default():
    """returns default space
    if we are using spaces, give the first one in the list
    otherwise give "questions", translated or not 
    """
    custom = askbot_settings.FORUM_SPACES
    if custom:
        return custom.split(',')[0].strip()
    elif django_settings.ASKBOT_TRANSLATE_URL:
        return _('questions')
    else:
        return 'questions'
