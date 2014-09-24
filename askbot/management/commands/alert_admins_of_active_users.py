from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import get_template
from askbot.models import Thread
from askbot import const
from askbot.conf import settings as askbot_settings
from django.conf import settings as django_settings
from django.utils.translation import ungettext
from django.utils.translation import activate as activate_language
from askbot import mail
from askbot.utils.classes import ReminderSchedule
from askbot.models.question import Thread
from askbot.utils.html import site_url
from django.template import Context
from datetime import datetime, timedelta
from collections import defaultdict
from optparse import make_option

class Command(BaseCommand):
    """management command that sends reminders
    about unanswered questions to all users
    """
    option_list = BaseCommand.option_list + (
        make_option('--extra-emails',
            action='store',
            type='str',
            dest='emails',
            default=None,
            help='additional email addresses, comma-separated'
        ),
        make_option('--days',
            action='store',
            type='int',
            dest='days',
            default=1,
            help='interval in days to count the users activity'
        )
    )

    def handle(self, **options):

        cutoff = datetime.now() - timedelta(options['days'])

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

        activate_language(django_settings.LANGUAGE_CODE)
        template = get_template('email/active_users_alert.html')
        body_text = template.render(Context(data))#todo: set lang
        subject_line = 'Users who asked more than 5 questions in last %d days' % options['days']

        mail.mail_moderators(subject_line=subject_line, body_text=body_text)
        if options['emails']:
            emails = map(lambda v: v.strip(), options['emails'].split())
            from_email = django_settings.DEFAULT_FROM_EMAIL
            send_mail(subject_line, body_text, from_email, emails)
