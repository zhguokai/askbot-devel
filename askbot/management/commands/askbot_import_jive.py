from askbot import models
from askbot.conf import settings as askbot_settings
from askbot.utils.console import ProgressBar
from askbot.utils.slug import slugify
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.forms import EmailField, ValidationError
from datetime import datetime

def parse_date(date_str):
    return datetime.strptime(date_str[:-8], '%Y/%m/%d %H:%M:%S')

class Command(BaseCommand):
    args = '<jive-dump.xml>'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        #relax certain settings
        askbot_settings.update('LIMIT_ONE_ANSWER_PER_USER', False)
        askbot_settings.update('MAX_COMMENT_LENGTH', 1000000)
        askbot_settings.update('MIN_REP_TO_LEAVE_COMMENTS', 1)
        self.bad_email_count = 0

    def handle(self, *args, **kwargs):
        assert len(args) == 1, 'Dump file name is required'
        xml = open(args[0], 'r').read() 
        try:
            import lxml
            soup = BeautifulSoup(xml, 'lxml')
        except ImportError:
            soup = BeautifulSoup(xml)

        self.import_users(soup.find_all('user'))
        self.import_forums(soup.find_all('forum'))

    @transaction.commit_manually
    def import_users(self, user_soup):
        """import users from jive to askbot"""

        message = 'Importing users:'
        for user in ProgressBar(iter(user_soup), len(user_soup), message):
            username = user.find('username').text
            real_name = user.find('name').text
            try:
                email = EmailField().clean(user.find('email').text)
            except ValidationError:
                email = 'unknown%d@example.com' % self.bad_email_count
                self.bad_email_count += 1
                
            joined_timestamp = parse_date(user.find('creationdate').text)
            user = models.User(
                username=username,
                email=email,
                real_name=real_name,
                date_joined=joined_timestamp
            )
            user.save()
            transaction.commit()

    def import_forums(self, forum_soup):
        """import forums by associating each with a special tag,
        and then importing all threads for the tag"""
        admin = models.User.objects.get(id=1)
        for forum in forum_soup:
            threads_soup = forum.find_all('thread')
            self.import_threads(threads_soup, forum.find('name').text)

    @transaction.commit_manually
    def import_threads(self, threads, tag_name):
        message = 'Importing threads for %s' % tag_name
        for thread in ProgressBar(iter(threads), len(threads), message):
            self.import_thread(thread, tag_name)
            transaction.commit()

    def import_thread(self, thread, tag_name):
        """import individual thread"""
        question_soup = thread.message
        title, body, timestamp, user = self.parse_post(question_soup)
        #post question
        question = user.post_question(
            title=title,
            body_text=body,
            timestamp=timestamp,
            tags=tag_name
        )
        #post answers
        if not question_soup.messagelist:
            return

        for answer_soup in question_soup.messagelist.find_all('message', recursive=False):
            title, body, timestamp, user = self.parse_post(answer_soup)
            answer = user.post_answer(
                question=question,
                body_text=body,
                timestamp=timestamp
            )
            comments = answer_soup.find_all('message')
            for comment in comments:
                title, body, timestamp, user = self.parse_post(comment)
                user.post_comment(
                    parent_post=answer,
                    body_text=body,
                    timestamp=timestamp
                )

    def parse_post(self, post):
        title = post.find('subject').text
        added_at = parse_date(post.find('creationdate').text)
        username = post.find('username').text
        body_node = post.find('messagebody')
        if body_node:
            body = post.find('messagebody').text
        else:
            raise Exception('Rename tags <Body> to <MessageBody> then clear the database and re-import')
        try:
            user = models.User.objects.get(username=username)
        except models.User.DoesNotExist:
            email = 'unknown%d@example.com' % self.bad_email_count
            self.bad_email_count += 1
            user = models.User(username=username, email=email)
            user.save()
        return title, body, added_at, user
