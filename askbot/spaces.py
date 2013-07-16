"""functions for managing Q&A spaces"""
from django.conf import settings as django_settings
from django.core.urlresolvers import reverse
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

def get_url(url_pattern_name, space=None, kwargs=None):
    """reverse url prefixed with space"""
    kwargs = kwargs or dict()
    kwargs['space'] = space or get_default()
    return reverse(url_pattern_name, kwargs=kwargs)
