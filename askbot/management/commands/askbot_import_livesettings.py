from askbot.conf import settings as askbot_settings
from django.conf import settings as django_settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils import translation
import re
import yaml

def update_setting(key, value, lang=None):
    try:
        askbot_settings.update(key, value, lang)
    except:
        print 'Failed to set %s' % key


class Command(BaseCommand):
    args = '<settings file in yaml format>'
    help = """Imports settings from a yaml file.
There are some requirements on the file, read below.

Example of the file:

APP_URL: http://example.com
WORDS_ASK_YOUR_QUESTION:
    en: Create issue
    de: 
WORDS_POST_YOUR_ANSWER: Add solution 

In the example above localized values are set
for the settings WORDS_ASK_YOUR_QUESTION for 
languages 'en' and 'de'

For WORDS_POST_YOUR_ANSWER only value
for the default language is set (given by the LANGUAGE_CODE in
the settings.py file).

Values can be strings, numbers or booleans (True/False)
"""

    def handle(self, *args, **kwargs):
        if len(args) != 1:
            raise CommandError('argument must be name of the settings dump module')
        filename = args[0]
        data = yaml.load(open(filename))

        translation.activate(django_settings.LANGUAGE_CODE)
        for key, value in data.items():
            if isinstance(value, basestring):
                update_setting(key, value)
            elif isinstance(value, dict):
                for lang, value in value.items():
                    update_setting(key, value, lang)
