from askbot.models import Feed
from askbot.models import Space
from askbot.models import Thread
from askbot.utils.console import ProgressBar
from django.conf import settings as django_settings
from django.core.management.base import NoArgsCommand
from django.contrib.sites.models import Site

"""examples:
#key - space id, value - space name
#here we create two question spaces
ASKBOT_SPACES = {
    1: 'support',
    2: 'development'
}
#key - site id, value - (site name, site domain)
#here we have two sites
ASKBOT_SITES = {
    1: ('public', 'public.example.com'),
    2: ('private', 'private.example.com')
}
#key - feed id, value - (feed name, site id, (space id list))
#two feeds, both named 'questions', associated with sites 1 and 2
#and fist one has space 1, while second - spaces 1 and 2
ASKBOT_FEEDS = {
    1: ('questions', 1, (1,)),
    2: ('questions', 2, (1, 2))
}
"""

SITES = getattr(django_settings, 'ASKBOT_SITES')
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
        for (site_id, site_data) in SITES.items():
            site = get_object_by_id(Site, site_id)
            site.name = site_data[0]
            site.domain = site_data[1]
            site.save()

        #create feeds
        for (feed_id, feed_data) in FEEDS.items():
            feed = get_object_by_id(Feed, feed_id)
            feed.name = feed_data[0]
            site_id = feed_data[1]
            space_ids = feed_data[2]
            feed.default_space = get_object_by_id(Space, space_ids[0])
            feed.site = get_object_by_id(Site, site_id)
            feed.save()

            for space_id in space_ids:
                space = get_object_by_id(Space, space_id)
                feed.add_space(space)

        #get site with lowest id:
        main_site = Site.objects.all().order_by('id')[0]
        #naive way to get the main feed for the site
        main_feed = Feed.objects.filter(
                                site=main_site
                            ).order_by('id')[0]

        threads = Thread.objects.all()
        count = threads.count()
        message = 'Adding all threads to the %s space' % main_site.name

        main_space = main_feed.default_space
        for thread in ProgressBar(threads.iterator(), count, message):
            main_space.questions.add(thread)
