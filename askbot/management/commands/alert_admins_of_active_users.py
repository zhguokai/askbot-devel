from django.core.management.base import NoArgsCommand
from django.template.loader import get_template
from askbot.models import Thread
from askbot import const
from askbot.conf import settings as askbot_settings
from django.utils.translation import ungettext
from askbot import mail
from askbot.utils.classes import ReminderSchedule
from askbot.models.question import Thread
from askbot.utils.html import site_url
from django.template import Context
from datetime import datetime, timedelta
from collections import defaultdict

DEBUG_THIS_COMMAND = False

class Command(NoArgsCommand):
    """management command that sends reminders
    about unanswered questions to all users
    """
    def handle_noargs(self, **options):

        cutoff = datetime.now() - timedelta(5)

        user_threads = defaultdict(set)
        for thread in Thread.objects.filter(added_at__gt=cutoff):
            question = thread._question_post()
            user = question.author
            user_threads[user].add(thread)

        for user in user_threads.keys():
            if len(user_threads[user]) <= 5:
                del user_threads[user]

        if len(user_threads) == 0:
            return

        data = {'user_threads': user_threads}

        template = get_template('email/active_users_alert.html')
        body_text = template.render(Context(data))#todo: set lang
        subject_line = 'Users who asked more than 5 questions in last 24 hours'

        if DEBUG_THIS_COMMAND:
            print "User: %s<br>\nSubject:%s<br>\nText: %s<br>\n" % \
                (user.email, subject_line, body_text)
        else:
            mail.mail_admins(subject_line=subject_line, body_text=body_text)
