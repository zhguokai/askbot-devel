from django.core.management.base import NoArgsCommand
from django.contrib.sites.models import Site
from askbot.conf import settings as askbot_settings
from askbot.models import Space
from askbot.models import Tag
from askbot.models import Thread
import askbot

def get_threads_counts(tag, site):
    """returns number of threads on current site
    and the total number of threads"""
    total_count = Thread.objects.filter(tags=tag).count()
    site_count = 0
    if askbot_settings.SPACES_ENABLED and askbot.is_multisite():
        spaces = Space.objects.get_for_site(site=site)
        threads = Thread.objects.filter(tags=tag, spaces__in=spaces)
        site_count = threads.distinct().count()
    return total_count, site_count

class Command(NoArgsCommand):
    def handle_noargs(self, *args, **kwargs):
        site = Site.objects.get_current()
        for tag in Tag.objects.all():
            total_count, site_count = get_threads_counts(tag, site)
            tag.used_count = total_count
            tag.save()

            if askbot.is_multisite():
                link = tag.get_site_link(site=site)
                link.set_used_count(site_count)
