from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings as django_settings
from django.utils import translation

from askbot.models import Thread
from askbot.utils.console import ProgressBar


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '-l',
            '--language',
            action='append',
            default=(django_settings.LANGUAGE_CODE,),
            help='Specify the languages for which the cache has to be rebuilt.'
        ),
    )

    def handle(self, **options):
        languages = options['language']
        for l in languages:
            translation.activate(l)
            message = 'Rebuilding {} thread summary cache'.format(l.upper())
            count = Thread.objects.count()
            for thread in ProgressBar(Thread.objects.iterator(),
                                      count, message):
                thread.update_summary_html()
