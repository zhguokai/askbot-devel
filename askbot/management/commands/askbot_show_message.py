from askbot.models import User
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import re

class Command(BaseCommand):
    """management command that sets a message to a user
    """
    help = 'Creates a message to users identified by user ids'
    option_list = BaseCommand.option_list + (
        make_option('-u', '--user-ids',
            action='store',
            dest='user_ids',
            default='',
            type='string',
            help='Space-separated ids of users to send this message'
        ),
        make_option('-m', '--message',
            action='store',
            dest='message',
            default='',
            type='string',
            help='Text of the message'
        )
    )

    def handle(self, *args, **options):

        #a simple pre-validation of the id list
        if re.match('^[\d+ ]+$', options['user_ids']) is None:
            raise CommandError('List of user ids must contain numbers, separated with spaces')
        
        user_ids = options['user_ids'].strip().split()

        found_ids = set()
        for user in User.objects.filter(id__in=user_ids):
            user.message_set.create(message=options['message'])
            found_ids.add(user.id)

        not_found_ids = set(user_ids) - found_ids
        if not_found_ids:
            print 'Ids %s do not exist' % not_found_ids
