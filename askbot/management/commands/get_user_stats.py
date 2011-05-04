import sys
import optparse
import datetime
from django.core.management.base import BaseCommand, CommandError
from askbot import models


def format_table_row(*cols, **kwargs):
        bits = list()
        for col in cols:
            bits.append(col)
        line = kwargs['format_string'] % tuple(bits)

        return line


class Command(BaseCommand):
    help = """Dump user reputation statistics."""

    option_list = BaseCommand.option_list 
    def handle(self, *args, **options):
        print 'User Stats for %s\n' % datetime.date.today()
        self.print_user_sub_counts()
        print ''

    def print_user_sub_counts(self):
        """prints list of users and their stats
        """
        users = models.User.objects.all().order_by('username')
        item_count = 0
        print '%-25s %4s %6s %6s %6s %6s %6s %6s %6s' % (
       'User', 'id', '# Q', '# A', 'Votes', 'Karma','Gold','Silver','Bronze')
        print '%-25s %4s %6s %6s %6s %6s %6s %6s %6s' % (
        '=========================', '====', '===', '===', '=====', '=====', '====', '======', '======')
        for user in users:
            user_string = '%-25s %4s' % (user.username, user.id)
            line = format_table_row(
                                user_string, user.questions.count(), user.answers.count(),
                                user.votes.count(), 
                                user.reputation, user.gold, user.silver, user.bronze,
                                format_string = '%-30s %6s %6s %6s %6s %6s %6s %6s'
                            )
            print line

