from optparse import make_option

from django.core.management import call_command
from django.utils.translation import activate as activate_language
from django.core.management.base import BaseCommand
from django.conf import settings

try:
    from haystack.management.commands.clear_index import Command as ClearCommand
    from haystack.management.commands.update_index import Command as UpdateCommand
    haystack_option_list = [option for option in UpdateCommand.base_options if option.get_opt_string() != '--verbosity'] + \
                  [option for option in ClearCommand.base_options if not option.get_opt_string() in ['--using', '--verbosity']]
except ImportError:
    haystack_option_list = []

class Command(BaseCommand):
    help = "Completely rebuilds the search index by removing the old data and then updating."
    base_options = [make_option("-l", "--language", action="store", type="string", dest="language",
                                help='Language to user, in language code format'),]
    option_list = list(BaseCommand.option_list) + haystack_option_list + base_options

    def handle(self, **options):
        lang_code = options.get('language', settings.LANGUAGE_CODE.lower())
        activate_language(lang_code)
        options['using'] = ['default_%s' % lang_code[:2],]
        call_command('rebuild_index', **options)
