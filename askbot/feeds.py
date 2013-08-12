from django.conf import settings as django_settings
from django.core.urlresolvers import reverse

#here we should be able to add more feeds
def get_default():
    if django_settings.ASKBOT_TRANSLATE_URL:
        return _('questions')
    else:
        return 'questions'

def get_feeds():
    if django_settings.ASKBOT_TRANSLATE_URL:
        return [_('questions'),]
    else:
        return ['questions',]

def get_url(url_pattern_name, feed=None, kwargs=None):
    """reverse url prefixed with feed"""
    kwargs = kwargs or dict()
    kwargs['feed'] = feed or get_default()
    return reverse(url_pattern_name, kwargs=kwargs)

def feed_exists(value):
    return value in get_feeds()
