from django.core.management.base import NoArgsCommand

from askbot.models import User


class Command(NoArgsCommand):
    def handle_noargs(self, *args, **kwargs):
        # Make sure all superusers have their status set to 'd'
        fixed = (User.objects
                 .filter(is_superuser=True)
                 .exclude(status='d')
                 .update(status='d'))

        # Make sure all normal users have their status not set to 'd'
        fixed += (User.objects
                  .filter(status='d')
                  .exclude(is_superuser=True)
                  .update(status='a'))

        self.stdout.write('Fixed the status of {0} users.'.format(fixed))
