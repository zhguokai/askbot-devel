from django.core import management
from django.contrib.staticfiles.management.commands.collectstatic import Command as CollectStatic
from askbot.conf import settings as askbot_settings

def increment_media_version():
    try:
        version = int(askbot_settings.MEDIA_RESOURCE_REVISION)
    except:
        version = 0
    askbot_settings.update('MEDIA_RESOURCE_REVISION', version + 1)


class Command(CollectStatic):
    """Extends the collectstatic command
    for Askbot so that the media resource revision is 
    automatically incremented"""

    def handle(self, *arguments, **options):
        increment_media_version()
        super(CollectStatic, self).handle(*arguments, **options)
