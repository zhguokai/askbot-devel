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
    help = """
Imports askbot livesettings from a yaml file.

example.yaml:

# This is a comment
# Use utf-8 throughout 
# Quote string values (just in case your string contains a yaml special character)
#
# Booleans:
# ------------------
#
GROUPS_ENABLED: True
#
#
# Integers:
# ------------------
#
MAX_VOTES_PER_USER_PER_DAY: 10
#
#
# Non-localized strings:
# ----------------------
#
GLOBAL_GROUP_NAME: "All"
#
#
# Localized strings:
# ------------------
#
# Set a string in default language (django settings.LANGUAGE_CODE):
QUESTION_INSTRUCTIONS: "Please use this page to ask a question to the group"
#
# Set a string in specific languages:
QUESTION_INSTRUCTIONS:
    en: "Please use this page to ask a question to the group"
    fr: "Se il vous pla\xeet utiliser cette page pour poser une question au groupe"
#
"""

    def handle(self, *args, **kwargs):
        if len(args) != 1:
            raise CommandError('argument must be name of the settings dump module')
        filename = args[0]
        data = yaml.load(open(filename))

        translation.activate(django_settings.LANGUAGE_CODE)
        for key, value in data.items():
            if isinstance(value, dict):
                for lang, value in value.items():
                    update_setting(key, value, lang)
            else:
                update_setting(key, value)
