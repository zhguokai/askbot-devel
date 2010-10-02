from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import User

#file_name = 'badge_log'
#format:
# username | message

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        file = open(file_name)
        lines = file.readlines()
        for line in lines:
            name, message = line.split(' | ')
            user = User.objects.get(username=name.strip())
            user.message_set.create(message=message.strip())
