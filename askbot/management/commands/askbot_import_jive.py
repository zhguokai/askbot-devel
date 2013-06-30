from askbot import models
from askbot.conf import settings as askbot_settings
from askbot.utils.console import ProgressBar
from askbot.utils.slug import slugify
from bs4 import BeautifulSoup
from django.conf import settings as django_settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.forms import EmailField, ValidationError
from django.utils import translation
from datetime import datetime
from optparse import make_option
import re

class DummyTransaction(object):
    @classmethod
    def commit(cls):
        pass

    @classmethod
    def commit_manually(cls, func):
        def decorated(*args, **kwargs):
            func(*args, **kwargs)
        return decorated

#transaction = DummyTransaction()

def jive_to_markdown(text):
    """convert jive forum markup to markdown
    using common sense guesswork
    """
    text = re.sub('(\n\n)+', '\n\n', text)#paragraph separators
    text = re.sub('\t', '    ', text)#tabs to four spaces
    text = re.sub('\n\s*>[^\n]+', '', text)#delete forum quotes
    text = re.sub('(?<!\n)\n', '\n    ', text)#force linebreaks via <pre>
    text = re.sub(r'\n\s*Edited by:[^\n]*(\n|$)', '\n', text)#delete "Edited by" comments
    text = re.sub(r'([^\n])\n(?!\n)', r'\1\n    ', text)#force linebreakes via <pre>
    text = re.sub(r'\n[ ]*([^\n]*{code}[^\n]*)\n', r'\n\1\n', text)#undo damage from above
    text = re.sub(r'{code}([^{]+){code}', r'`\1`', text)
    return text

def parse_date(date_str):
    return datetime.strptime(date_str[:-8], '%Y/%m/%d %H:%M:%S')

def turn_first_company_user_to_admin(domain):
    company_users = models.User.objects.filter(
                        email__endswith='@' + domain
                    ).order_by('id')
    if company_users.count() == 0:
        return None

    user = company_users[0]
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user

def thread_get_answer_from_company(thread, domain):
    answers = thread.posts.filter(
                        post_type='answer'
                    ).select_related(
                        'author__email'
                    )
    for answer in answers:
        if answer.author.email.endswith('@' + domain):
            return answer
    return None

def thread_find_first_comment_from_company(thread, domain):
    comments = thread.posts.filter(
                        post_type='comment'
                    ).select_related(
                        'author__email'
                    ).order_by('added_at')
    for comment in comments:
        if comment.author.email.endswith('@' + domain):
            return comment
    return None

COMPANY_DOMAIN_HELP = """If used - first response from user with that domain
then first response in each question from user with matching email address
will be posted as answer and accepted as correct. Also, first user
with a matching email address will be a site administrator."""

class Command(BaseCommand):
    args = '<jive-dump.xml>'
    option_list = BaseCommand.option_list + (
        make_option('--company-domain',
            action = 'store',
            type = 'str',
            dest = 'company_domain',
            default = None,
            help = COMPANY_DOMAIN_HELP
        ),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        #relax certain settings
        askbot_settings.update('LIMIT_ONE_ANSWER_PER_USER', False)
        askbot_settings.update('MAX_COMMENT_LENGTH', 1000000)
        askbot_settings.update('MIN_REP_TO_INSERT_LINK', 1)
        askbot_settings.update('MIN_REP_TO_SUGGEST_LINK', 1)
        askbot_settings.update('COMMENTS_EDITOR_TYPE', 'rich-text')
        askbot_settings.update('MARKUP_CODE_FRIENDLY', True)
        self.bad_email_count = 0

    def handle(self, *args, **kwargs):
        translation.activate(django_settings.LANGUAGE_CODE)
        assert len(args) == 1, 'Dump file name is required'
        xml = open(args[0], 'r').read() 
        soup = BeautifulSoup(xml, ['lxml', 'xml'])

        self.import_users(soup.find_all('User'))
        self.import_forums(soup.find_all('Forum'))
        if kwargs['company_domain']:
            self.promote_company_replies(kwargs['company_domain'])
        models.Message.objects.all().delete()

    @transaction.commit_manually
    def promote_company_replies(self, domain):
        admin = turn_first_company_user_to_admin(domain)
        if admin is None:
            print "Note: did not find any users with email matching %s" % domain
            return
        message = 'Promoting company replies to accepted answers:'
        threads = models.Thread.objects.all()
        count = threads.count()
        for thread in ProgressBar(threads.iterator(), count, message):
            answer = thread_get_answer_from_company(thread, domain)

            if answer == None:
                comment = thread_find_first_comment_from_company(thread, domain)
                if comment:
                    admin.repost_comment_as_answer(comment)
                    answer = comment

            if answer:
                admin.accept_best_answer(answer=answer, force=True)

            transaction.commit()
        transaction.commit()

    @transaction.commit_manually
    def import_users(self, user_soup):
        """import users from jive to askbot"""

        message = 'Importing users:'
        for user in ProgressBar(iter(user_soup), len(user_soup), message):
            username = user.find('Username').text
            real_name = user.find('Name').text
            try:
                email = EmailField().clean(user.find('Email').text)
            except ValidationError:
                email = 'unknown%d@example.com' % self.bad_email_count
                self.bad_email_count += 1
                
            joined_timestamp = parse_date(user.find('CreationDate').text)
            user = models.User(
                username=username,
                email=email,
                real_name=real_name,
                date_joined=joined_timestamp
            )
            user.set_unusable_password()
            user.save()
            transaction.commit()

    def import_forums(self, forum_soup):
        """import forums by associating each with a special tag,
        and then importing all threads for the tag"""
        admin = models.User.objects.get(id=1)
        print 'Have %d forums' % len(forum_soup)
        for forum in forum_soup:
            threads_soup = forum.find_all('Thread')
            self.import_threads(threads_soup, forum.find('Name').text)

    @transaction.commit_manually
    def import_threads(self, threads, tag_name):
        message = 'Importing threads for %s' % tag_name
        for thread in ProgressBar(iter(threads), len(threads), message):
            self.import_thread(thread, tag_name)
            transaction.commit()

    def import_thread(self, thread, tag_name):
        """import individual thread"""
        question_soup = thread.find('Message')
        title, body, timestamp, user = self.parse_post(question_soup)
        #post question
        question = user.post_question(
            title=title,
            body_text=body,
            timestamp=timestamp,
            tags=tag_name,
            language=django_settings.LANGUAGE_CODE
        )
        #post answers
        message_list = question_soup.find_all('MessageList', recursive=False)
        if len(message_list) == 0:
            return

        for answer_soup in message_list[0].find_all('Message', recursive=False):
            title, body, timestamp, user = self.parse_post(answer_soup)
            answer = user.post_answer(
                question=question,
                body_text=body,
                timestamp=timestamp
            )
            comments = answer_soup.find_all('Message')
            for comment in comments:
                title, body, timestamp, user = self.parse_post(comment)
                user.post_comment(
                    parent_post=answer,
                    body_text=body,
                    timestamp=timestamp
                )

    def parse_post(self, post):
        title = post.find('Subject').text
        added_at = parse_date(post.find('CreationDate').text)
        username = post.find('Username').text
        body = jive_to_markdown(post.find('Body').text)
        try:
            user = models.User.objects.get(username=username)
        except models.User.DoesNotExist:
            email = 'unknown%d@example.com' % self.bad_email_count
            self.bad_email_count += 1
            user = models.User(username=username, email=email)
            user.save()
        return title, body, added_at, user
