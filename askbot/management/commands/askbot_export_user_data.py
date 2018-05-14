"""Exports data for a user with given ID"""
from optparse import make_option
from django.management.base import BaseCommand, CommandError
from askbot.models import User

class Command(BaseCommand):
    """Exports data for a user given his or her ID"""

    option_list = BaseCommand.option_list + (
        make_option('--user-id',
                    action='store',
                    type='int',
                    dest='user_id',
                    default=None,
                    help='ID of the user whose data we will export'),
        make_option('--file',
                    action='store',
                    type='str',
                    default=None,
                    help='Path to the output file, absolute or relative to CWD')
                                            )

    def handle(self, *args, **options):
        """Does the job of the command"""
        uid = options['user_id']

        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            raise CommandError('User with id {} does not exist'.format(uid))

        # collect user account data
        about
        date of birth
        username
        account url
        email
        avatar, if uploaded

        # collect questions
        # extract question image urls

        # collect answers
        # extract answer image urls

        # collect comments
        # extract comment image urls

        # save json file

        # make directory for images
        # try to find images in upfiles and copy them

        # zip the images dir and the json file


