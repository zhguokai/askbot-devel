from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.conf import settings as django_settings
from django.core.urlresolvers import reverse
from askbot.conf import settings as askbot_settings
from askbot.models.base import BaseQuerySetManager

class SpaceManager(BaseQuerySetManager):

    def get_default(self):
        """returns default space
        if we are using spaces, give the first one in the list
        otherwise give "questions", translated or not
        """
        custom = askbot_settings.FORUM_SPACES
        if askbot_settings.SPACES_ENABLED and custom.strip():
            return custom.split(',')[0].strip()
        return None

    def get_spaces(self):
        """returns list of available spaces"""
        custom = askbot_settings.FORUM_SPACES
        if askbot_settings.SPACES_ENABLED and custom.strip():
            return map(lambda v: v.strip(), custom.split(','))

    def add_space(self, name):
        """adds space if it does not exist"""
        if not space_exists(name):
            spaces_string = askbot_settings.FORUM_SPACES
            enabled_spaces = map(lambda v: v.strip(), spaces_string.split(','))
            if name not in enabled_spaces:
                enabled_spaces.append(name)
                askbot_settings.update('FORUM_SPACES', ', '.join(enabled_spaces))


    def space_exists(self, value):
        return value in get_spaces()

class FeedManager(BaseQuerySetManager):

    def get_default(self):
        if django_settings.ASKBOT_TRANSLATE_URL:
            return _('questions')
        else:
            return 'questions'

    def get_feeds(self):
        if django_settings.ASKBOT_TRANSLATE_URL:
            return [_('questions'),]
        else:
            return ['questions',]

    def get_url(self, url_pattern_name, feed=None, kwargs=None):
        """reverse url prefixed with feed"""
        kwargs = kwargs or dict()
        kwargs['feed'] = feed or self.get_default()
        return reverse(url_pattern_name, kwargs=kwargs)

    def feed_exists(self, value):
        return value in self.get_feeds()

class Space(models.Model):
    name = models.CharField(max_length=100)
    questions = models.ManyToManyField('Thread')

    objects = SpaceManager()

    class Meta:
        app_label = 'askbot'

    def __unicode__(self):
        return "Space %s" % self.name

class Feed(models.Model):
    #TODO: url should never change add validation.
    url = models.CharField(max_length=50)
    redirect = models.ForeignKey('self')
    default_space = models.ForeignKey(Space)

    site = models.ForeignKey(Site)
    objects = FeedManager()

    class Meta:
        app_label = 'askbot'

    def __unicode__(self):
        return "Feed %s" % self.url

class FeedToSpace(models.Model):
    space = models.ForeignKey(Space)
    feed = models.ForeignKey(Feed)

    class Meta:
        app_label = 'askbot'
        unique_together = ('space', 'feed')

class GroupToSpace(models.Model):
    group = models.ForeignKey('Group')
    space = models.ForeignKey(Space)

    class Meta:
        app_label = 'askbot'
        unique_together = ('space', 'group')

def get_feed_url(url_pattern_name, feed=None, kwargs=None):
    return Feed.objects.get_url(url_pattern_name, feed, kwargs)
