from askbot.conf import settings as askbot_settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
import re

class Command(BaseCommand):
    args = '<settings_dump_module>'
    help = """Imports live settings saved into a file.
There are some requirements on the file, read below.

Settings dump module is a file containing output of the url
/settings/export/ with one modification: - the settings dictionary is 
assigned to the value called "settings", i.e.:

settings = {1: {...}}

It is assumed that settings dictionary contains exactly one key:
site_id -> value
"""

    def handle(self, *args, **kwargs):
        if len(args) != 1:
            raise CommandError('argument must be name of the settings dump module')
        filename = args[0]
        modname = re.sub(r'\.py$', '', filename)
        modname = modname.replace('/', '.')
        modname = modname.replace('\\', '.')

        mod = __import__(modname, locals(), globals(), ['settings'], -1)
        livesettings = mod.settings.values()[0]
        for settings_group in livesettings.values():
            for name, value in settings_group.items():
                try:
                    askbot_settings.update(name, value)
                except:
                    print "Failed to set %s" % name
