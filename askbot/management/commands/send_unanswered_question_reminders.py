import datetime
import optparse
from django.core.management.base import BaseCommand
from django.conf import settings as django_settings
from askbot import models
from askbot import const
from askbot.conf import settings as askbot_settings
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from askbot.utils import mail
from askbot.models.question import get_tag_summary_from_questions


class Command(BaseCommand):
    help = 'Send Email reminder for unanswered emails'

    option_list = BaseCommand.option_list + (
       optparse.make_option(
          '-d',
          '--debug',
          action = 'store_true',
          default = False,
          dest = 'debug',
          help = 'Do NOT sent emails, but print what they would be'
       ),
       optparse.make_option(
          '-f',
          '--force-email',
          action = 'store_true',
          default = False,
          dest = 'force_email',
          help = 'Send emails even if emails were sent recently'
       ),
       optparse.make_option(
          '-i',
          '--ignore-dates',
          action = 'store_true',
          default = False,
          dest = 'ignore_dates',
          help = 'Select questions even if they are outside the date exclusion range'
       ),
    )
    def handle(self, *args, **options):
        DEBUG_THIS_COMMAND = False
        FORCE_EMAIL = False
        IGNORE_DATES = False

        if askbot_settings.ENABLE_UNANSWERED_REMINDERS == False:
            return

        if options['ignore_dates']:
           IGNORE_DATES = True
           FORCE_EMAIL = True
        if options['debug']:
           DEBUG_THIS_COMMAND = True
        if options['force_email']:
           FORCE_EMAIL = True

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

        if IGNORE_DATES:
            questions = models.Question.objects.exclude(
                                        closed = True
                                    ).exclude(
                                        deleted = True
                                    ).filter(
                                        added_at__lt = start_cutoff_date
                                    ).filter(
                                        answer_count = 0
                                    ).order_by('-added_at')
        else: 
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
                        # Only send email if minimum delay between emails has been met
                        if not DEBUG_THIS_COMMAND and not FORCE_EMAIL:
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

            body_text = '<p>This email is sent as a reminder that the following questions do not have ' \
                        'an answer. If you can provide an answer, please click on the link and share ' \
                        'your knowlege.</p><hr><p><b>Summary List</b></p>'

            tag_list = {}
            now = datetime.datetime.now()
            # Build list of Tags
            for question in final_question_list:
               tag_names = question.get_tag_names()
               tag_string = ""
               days = now - question.added_at
               for tag in tag_names:
                 tag_string += tag + ", "
                 if tag in tag_list:
                    tag_list[tag].append((question, days))
                 else:
                    tag_list[tag] = [(question, now - question.added_at)]

               body_text += '<li><a href="%s%s?sort=latest">(%02d days old) %s [%s]</a></li>' \
                      % (
                          askbot_settings.APP_URL,
                          question.get_absolute_url(),
                          days.days,
                          question.title,
                          tag_string[:-2]
                      )

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

            body_text += "<hr><p><b>List ordered by Tags</b></p><br>"
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
                print "User: %s - %s" % (user.email, subject_line)
                mail.send_mail(
                    subject_line = subject_line,
                    body_text = body_text,
                    recipient_list = (user.email,)
                )
