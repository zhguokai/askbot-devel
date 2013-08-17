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
        space_name = askbot_settings.DEFAULT_SPACE_NAME
        current_site = Site.objects.get_current()
        try:
            return self.get_query_set().get(name=space_name,
                                            site=current_site)
        except Space.DoesNotExist:
            return self.get_query_set().create(name=space_name,
                                               site=current_site)

    def space_exists(self, value):
        current_site = Site.objects.get_current()
        self.get_query_set.filter(name=value,
                                  site=current_site).exists()

class FeedManager(BaseQuerySetManager):

    def get_default(self):
        default_url = askbot_settings.DEFAULT_FEED_NAME
        current_site = Site.objects.get_current()
        try:
            return self.get_query_set().get(name=default_url, site=current_site)
        except Feed.DoesNotExist:
            default_space = Space.objects.get_default()
            return self.get_query_set().create(name=default_url,
                                               default_space=default_space,
                                               site=current_site
                                              )

    def get_feeds(self):
        current_site = Site.objects.get_current()
        if django_settings.ASKBOT_TRANSLATE_URL:
            return map(_, self.get_query_set().filter(site=current_site).values_list('name', flat=True))
        else:
            return self.get_query_set().filter(site=current_site).values_list('name', flat=True)

    def get_url(self, url_pattern_name, feed=None, kwargs=None):
        """reverse url prefixed with feed"""
        kwargs = kwargs or dict()
        if type(feed) is type(Feed):
            kwargs['feed'] = feed.name
        elif type(feed) in (unicode, str):
            kwargs['feed'] = feed
        else:
            kwargs['feed'] = self.get_default().name

        return reverse(url_pattern_name, kwargs=kwargs)

    def feed_exists(self, value):
        return self.get_query_set().filter(name=value).exists()

class Space(models.Model):
    name = models.CharField(max_length=100)
    questions = models.ManyToManyField('Thread')

    site = models.ForeignKey(Site)
    objects = SpaceManager()

    class Meta:
        app_label = 'askbot'
        unique_together = ('name', 'site')

    def __unicode__(self):
        return "Space %s" % self.name

class Feed(models.Model):
    #TODO: url should never change add validation.
    name = models.CharField(max_length=50)
    default_space = models.ForeignKey(Space)
    redirect = models.ForeignKey('self', null=True, blank=True)

    site = models.ForeignKey(Site)
    objects = FeedManager()

    class Meta:
        app_label = 'askbot'
        unique_together = ('name', 'site')

    def __unicode__(self):
        return "Feed %s" % self.name


    def get_spaces(self):
        feed_to_space_list = [feedtospace.space for feedtospace in \
                self.feedtospace_set.filter(space__site=self.site).exclude(space=self.default_space)]
        feed_to_space_list.append(self.default_space)
        return feed_to_space_list

    def add_space(self, space):
        feed_to_space = FeedToSpace.objects.create(feed=self, space=space)
        self.feedtospace_set.add(feed_to_space)

    def thread_belongs_to_feed(self, thread):
        return thread.space_set.filter(feed=self).exists()

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
