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

def get_object_by_id(object_class, object_id):
    try:
        return object_class.objects.get(id=object_id)
    except object_class.DoesNotExist:
        return object_class(id=object_id)

class Command(NoArgsCommand):
    def handle_noargs(self, **kwargs):
        space1 = get_object_by_id(Space, 1)
        space1.name = SITE1_NAME
        space1.save()

        space2 = get_object_by_id(Space, 2)
        space2.name = SITE2_NAME
        space2.save()

        site1 = get_object_by_id(Site, 1)
        site1.name = SITE1_NAME
        site1.domain = SITE1_DOMAIN
        site1.save()

        feed1 = get_object_by_id(Feed, 1)
        feed1.name = 'questions'
        feed1.default_space = space1
        feed1.site = site1
        feed1.save()
        feed1.add_space(space1)
        feed1.add_space(space2)

        site2 = get_object_by_id(Site, 2)
        site2.name = SITE2_NAME
        site2.domain = SITE2_DOMAIN
        site2.save()

        feed2 = get_object_by_id(Feed, 2)
        feed2.name = 'questions'
        feed2.default_space = space2
        feed2.site = site2
        feed2.save()
        feed2.add_space(space2)

        threads = Thread.objects.all()
        count = threads.count()
        message = 'Adding all threads to the %s space' % SITE1_NAME

        for thread in ProgressBar(threads.iterator(), count, message):
            space1.questions.add(thread)
