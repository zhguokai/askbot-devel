from django.core.management.base import NoArgsCommand
from askbot.models import Activity
from askbot.models import User
from askbot import const

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        username = 'Evgeny'
        user = User.objects.get(username = username)

        response_activity_types = const.RESPONSE_ACTIVITY_TYPES_FOR_DISPLAY
        
        #delete all response notifications as he has seen these
        response_activities = Activity.objects.filter(
                                receiving_users = user,
                                activity_type__in = response_activity_types
                            )

        for activity in response_activities:
            activity.receiving_users.remove(user)
        user.response_count = 0
        user.save()

        #delete all hanging mentions - i.e. those whose 
        #content object is gone

        mentions = Activity.objects.get_mentions(
                                        mentioned_whom = user
                                    )
        for mention in mentions:
            try:
                print mention.content_object
            except:
                print 'object throws error'

