"""functions for managing Q&A spaces"""
from django.conf import settings as django_settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from askbot.conf import settings as askbot_settings

def add_space(name):
    """adds space if it does not exist"""
    if not space_exists(name):
        spaces_string = askbot_settings.FORUM_SPACES
        enabled_spaces = map(lambda v: v.strip(), spaces_string.split(','))
        if name not in enabled_spaces:
            enabled_spaces.append(name)
            askbot_settings.update('FORUM_SPACES', ', '.join(enabled_spaces))

def get_default():
    """returns default space
    if we are using spaces, give the first one in the list
    otherwise give "questions", translated or not 
    """
    custom = askbot_settings.FORUM_SPACES
    if askbot_settings.SPACES_ENABLED and custom.strip():
        return custom.split(',')[0].strip()
    elif django_settings.ASKBOT_TRANSLATE_URL:
        return _('questions')
    else:
        return 'questions'

def get_spaces():
    """returns list of available spaces"""
    custom = askbot_settings.FORUM_SPACES
    if askbot_settings.SPACES_ENABLED and custom.strip():
        return map(lambda v: v.strip(), custom.split(','))
    elif django_settings.ASKBOT_TRANSLATE_URL:
        return [_('questions'),]
    else:
        return ['questions',]

def get_url(url_pattern_name, space=None, kwargs=None):
    """reverse url prefixed with space"""
    kwargs = kwargs or dict()
    kwargs['space'] = space or get_default()
    return reverse(url_pattern_name, kwargs=kwargs)

def space_exists(value):
    return value in get_spaces()
