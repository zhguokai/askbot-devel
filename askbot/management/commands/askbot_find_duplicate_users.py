from askbot.models import User
from askbot.deps.django_authopenid.models import UserAssociation
from collections import defaultdict
from django.core.management.base import NoArgsCommand

def print_users(users):
    """prints data for the users"""
    for u in users:
        print '%d\t%s\t%s' % (u.id, u.username, u.email)

def get_repeating_values(cls, field_name):
    values = cls.objects.values_list(field_name, flat=True)
    variants = defaultdict(list)
    repeats = set()
    for value in values:
        base = value.lower()
        variants[base] += 1
        if variants[base] > 1:
            repeats.add(base)
    return repeats

class Command(NoArgsCommand):
    help = """Prints summary about users with duplicate email addresses,
    usernames, login methods, regardless of the letter case register"""

    def handle_noargs(self, **opts):
        #find email address dupes
        print 'Looking for users with duplicate emails:'
        emails = get_repeating_values(User, 'email')
        for email in emails:
            users = User.objects.filter(email__iexact=email)
            print_users(users)
        if len(emails) == 0:
            print 'Not found'

        print '\nLooking for users with duplicate username:'
        names = get_repeating_values(User, 'email')
        for name in names:
            users = User.objects.filter(username__iexact=name)
            print_users(users)
        if len(names) == 0:
            print 'Not found'

        print '\nLooking for users with duplicate login associations'
        logins = get_repeating_values(UserAssociation, 'openid_url')
        for login in logins:
            associations = UserAssociation.objects.filter(openid_url__iexact=login)
            users = [assoc.user for assoc in associations]
            print_users(users)
        if len(logins) == 0:
            print 'Not found'
