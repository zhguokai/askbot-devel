import datetime
from django.core.management.base import NoArgsCommand
from django.conf import settings as django_settings
from askbot import models
from askbot import const
from askbot.conf import settings as askbot_settings
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from askbot.utils import mail
from askbot.models.question import get_tag_summary_from_questions

DEBUG_THIS_COMMAND = False

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        if askbot_settings.ENABLE_UNANSWERED_REMINDERS == False:
            return
        #get questions without answers, excluding closed and deleted
        #order it by descending added_at date
        wait_period = datetime.timedelta(
            askbot_settings.DAYS_BEFORE_SENDING_UNANSWERED_REMINDER
        )
        start_cutoff_date = datetime.datetime.now() - wait_period

        recurrence_delay = datetime.timedelta(
            askbot_settings.UNANSWERED_REMINDER_FREQUENCY
        )
        max_emails = askbot_settings.MAX_UNANSWERED_REMINDERS
        end_cutoff_date = start_cutoff_date - (max_emails - 1)*recurrence_delay

        questions = models.Question.objects.exclude(
                                        closed = True
                                    ).exclude(
                                        deleted = True
                                    ).filter(
                                        added_at__lt = start_cutoff_date
                                    ).exclude(
                                        added_at__lt = end_cutoff_date
                                    ).filter(
                                        answer_count = 0
                                    ).order_by('-added_at')
        #for all users, excluding blocked
        #for each user, select a tag filtered subset
        #format the email reminder and send it
        for user in models.User.objects.exclude(status = 'b'):
            # Sanity check to catch invalid email
            if len(user.email) < 5:
                continue

            user_questions = questions.exclude(author = user)
            user_questions = user.get_tag_filtered_questions(
                                                questions = user_questions,
                                                context = 'email'
                                            )

            final_question_list = list()
            #todo: rewrite using query set filter
            #may be a lot more efficient
            for question in user_questions:
                activity_type = const.TYPE_ACTIVITY_UNANSWERED_REMINDER_SENT
                try:
                    activity = models.Activity.objects.get(
                        user = user,
                        question = question,
                        activity_type = activity_type
                    )
                    now = datetime.datetime.now()
                    if now < activity.active_at + recurrence_delay:
                        if not DEBUG_THIS_COMMAND:
                            continue
                except models.Activity.DoesNotExist:
                    activity = models.Activity(
                        user = user,
                        question = question,
                        activity_type = activity_type,
                        content_object = question,
                    )
                activity.active_at = datetime.datetime.now()
                activity.save()
                final_question_list.append(question)

            question_count = len(final_question_list)
            if question_count == 0:
                    continue

            tag_summary = get_tag_summary_from_questions(final_question_list)
            tag_list = {}
            now = datetime.datetime.now()
            # Build list of Tags
            for question in final_question_list:
               tag_names = question.get_tag_names()
               for tag in tag_names:
                 if tag in tag_list:
                    tag_list[tag].append((question, now - question.added_at))
                 else:
                    tag_list[tag] = [(question, now - question.added_at)]

            tag_keys = tag_list.keys()
            tag_keys.sort()
            subject_line = ungettext(
                '%(question_count)d unanswered question about %(topics)s',
                '%(question_count)d unanswered questions about %(topics)s',
                question_count
            ) % {
                'question_count': question_count,
                'topics': tag_summary
            }

            body_text = '<p>This email is sent as a reminder that the following questions do not have ' \
                        'an answer. If you can provide an answer, please click on the link and share ' \
                        'your knowlege.</p<hr>'

            for tag in tag_keys:
                body_text += '<p><b>' + tag + '</b></p><ul>'
                for question in tag_list[tag]:
                    body_text += '<li><a href="%s%s?sort=latest">(%02d days old) %s</a></li>' \
                            % (
                                askbot_settings.APP_URL,
                                question[0].get_absolute_url(),
                                question[1].days,
                                question[0].title
                            )
                body_text += '</ul>\n'

            if DEBUG_THIS_COMMAND:
                print "User: %s<br>\nSubject:%s<br>\nText: %s<br>\n" % \
                    (user.email, subject_line, body_text)
            else:
                mail.send_mail(
                    subject_line = subject_line,
                    body_text = body_text,
                    recipient_list = (user.email,)
                )
