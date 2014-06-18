from django.core.management.base import NoArgsCommand
from askbot.models import User
from askbot.models import UserProfile
from askbot.models import init_askbot_user_profile

class Command(NoArgsCommand):
    """a command to initialize missing askbot user profiles"""
    def handle_noargs(self, **kwargs):
        for user in User.objects.all():
            if UserProfile.objects.filter(auth_user=user).exists():
                continue
            try:
                init_askbot_user_profile(user)
            except Exception, e:
                print unicode(e).encode('utf-8')
