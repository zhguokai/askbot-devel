from askbot.models import Feed
from askbot.models import Space
from askbot.models import Thread
from askbot.utils.console import ProgressBar
from django.conf import settings as django_settings
from django.core.management.base import NoArgsCommand
from django.contrib.sites.models import Site

SITE1_DOMAIN = getattr(django_settings, 'SITE1_DOMAIN', 'windriver.askbot.com')
SITE1_NAME = getattr(django_settings, 'SITE1_NAME', 'windriver')
SITE2_DOMAIN = getattr(django_settings, 'SITE2_DOMAIN', 'intel.askbot.com')
SITE2_NAME = getattr(django_settings, 'SITE2_NAME', 'intel')

"""examples:
#key - space id, value - space name
ASKBOT_SPACES = {
    1: 'support',
    2: 'development'
}
#key - site id, value - (site name, site domain)
ASKBOT_SITES = {
    1: ('public', 'public.example.com'),
    2: ('private', 'private.example.com')
}
#key - feed id, value - (feed name, site id, (space id list))
ASKBOT_FEEDS = {
    1: ('questions', 1, (1,)),
    2: ('questions', 2, (1, 2))
}
"""

SPACES = getattr(django_settings, 'ASKBOT_SPACES')
FEEDS = getattr(django_settings, 'ASKBOT_FEEDS')

def get_object_by_id(object_class, object_id):
    try:
        return object_class.objects.get(id=object_id)
    except object_class.DoesNotExist:
        return object_class(id=object_id)

class Command(NoArgsCommand):
    def handle_noargs(self, **kwargs):

        #create spaces
        for (space_id, space_name) in SPACES.items():
            space = get_object_by_id(Space, space_id)
            space.name = space_name
            space.save()
            
        #create sites
        for (site_id, site_data) in SITES.items()
            site = get_object_by_id(Site, site_id)
            site.name = site_data[0]
            site.domain = site_data[1]
            site.save()

        #create feeds
        for (feed_id, feed_data) in FEEDS.items():
            feed = get_object_by_id(Feed, 1)
            feed.name = 'questions'
            feed.default_space = space1
            feed.site = site1
            feed.save()

            for space_id in feed_data[1:]:
                space = get_object_by_id(Space, space_id)
                feed.add_space(space)

        threads = Thread.objects.all()
        count = threads.count()
        message = 'Adding all threads to the %s space' % SITE1_NAME

        for thread in ProgressBar(threads.iterator(), count, message):
            space1.questions.add(thread)
