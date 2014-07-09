from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.conf import settings as django_settings
from django.core.cache import cache
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
        try:
            return self.get_query_set().get(name=space_name)
        except Space.DoesNotExist:
            return self.get_query_set().create(name=space_name)

    def space_exists(self, value):
        self.get_query_set.filter(name=value).exists()

    def get_for_site(self, site=None):
        """retuns spaces available in the given site
        results are cached
        """
        site = site or Site.objects.get_current()
        cache_key = u'askbot-spaces-%s' % unicode(site)
        spaces = cache.get(cache_key)
        if spaces is None:
            site = site or Site.objects.get_current()
            site_feeds = Feed.objects.filter(site=site)
            spaces = set()
            for site_feed in site_feeds:
                spaces |= set(site_feed.get_spaces())
            cache.set(cache_key, spaces)
        return spaces


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
        current_site = Site.objects.get_current()
        return self.get_query_set().filter(
                                    name=value,
                                    site=current_site
                                ).exists()

class Space(models.Model):
    name = models.CharField(max_length=100)
    questions = models.ManyToManyField('Thread', related_name='spaces')

    objects = SpaceManager()

    class Meta:
        app_label = 'askbot'

    def __unicode__(self):
        return "Space %s (id=%d)" % (self.name, self.id)

    def get_default_ask_group_id(self):
        """returns id of group to which question must be asked by default
        within this space, or None
        """
        #todo: implement this on the level of models
        if askbot_settings.GROUPS_ENABLED:
            spaces_settings = getattr(django_settings, 'ASKBOT_SPACES', None)
            if spaces_settings:
                space_settings = spaces_settings.get(self.id, None)
                if space_settings:
                    if len(space_settings) > 1:
                        return space_settings[1]
        return None

class Feed(models.Model):
    #TODO: url should never change add validation.
    name = models.CharField(max_length=50)
    default_space = models.ForeignKey(Space)
    redirect = models.ForeignKey('self', null=True, blank=True)

    site = models.ForeignKey(Site, related_name='askbot_feeds')
    objects = FeedManager()

    class Meta:
        app_label = 'askbot'
        unique_together = ('name', 'site')

    def __unicode__(self):
        return "Feed %s@%s" % (self.name, self.site.name)


    def get_spaces(self):
        feed_to_space_list = [space_link.space for space_link in \
                self.space_links.exclude(space=self.default_space)]
        feed_to_space_list.append(self.default_space)
        return feed_to_space_list

    def add_space(self, space):
        link, created = FeedToSpace.objects.get_or_create(feed=self, space=space)
        self.space_links.add(link)

    def thread_belongs_to_feed(self, thread):
        feed_spaces = set(self.get_spaces())
        thread_spaces = set(thread.spaces.all())
        return len(feed_spaces & thread_spaces) > 0

class FeedToSpace(models.Model):
    space = models.ForeignKey(Space, related_name='feed_links')
    feed = models.ForeignKey(Feed, related_name='space_links')

    class Meta:
        app_label = 'askbot'
        unique_together = ('space', 'feed')

class GroupToSpace(models.Model):
    group = models.ForeignKey('Group')
    space = models.ForeignKey(Space)

    class Meta:
        app_label = 'askbot'
        unique_together = ('space', 'group')

"""
class AskbotSite(models.Model):
    django_site = models.OneToOneField(Site, related_name='askbot_site')
    protocol = models.CharField(max_length=8, default='http')
    base_url = models.CharField(max_length=128, default='/')

    class Meta:
        app_label = 'askbot'
        db_table = 'askbot_site'

    def get_absolute_url(self):
        return self.protocol + '://' + self.domain + self.base_url
"""

def get_feed_url(url_pattern_name, feed=None, kwargs=None):
    return Feed.objects.get_url(url_pattern_name, feed, kwargs)

def get_site_ids():
    """get ids of active askbot sites"""
    site_id = django_settings.SITE_ID
    return getattr(django_settings, 'ASKBOT_SITE_IDS', [site_id,])

def get_site_name(site_id):
    """get site name by site id"""
    site_settings = getattr(django_settings, 'ASKBOT_SITES', None)
    if site_settings:
        site_info = site_settings[site_id]
        if isinstance(site_info, basestring):
            return site_info
        else:
            return site_info[0]
    else:
        from django.contrib.sites.models import Site
        return Site.objects.get(id=site_id).name

def get_default_space(site_id):
    """get default space for given site id"""
    feed_settings = django_settings.ASKBOT_FEEDS.values()
    for setting in feed_settings:
        if setting[1] == site_id:
            return Space.objects.get(id=setting[2][0])
