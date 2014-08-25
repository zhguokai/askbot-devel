"""WARNING: 
This command is incomplete, current awards only
Civic Duty badge
"""

from askbot.models import badges
from askbot.models import User
from askbot.models import Vote
import datetime
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    def handle_noargs(self, *args, **kwargs):
        now = datetime.datetime.now()
        for user in User.objects.all():
            try:
                #get last vote
                vote = Vote.objects.filter(user=user).order_by('-id')[0]
            except IndexError:
                #user did not vote
                continue
            else:
                cd = badges.CivicDuty()
                cd.consider_award(
                            actor=user,
                            context_object=vote.voted_post,
                            timestamp=now
                        )
