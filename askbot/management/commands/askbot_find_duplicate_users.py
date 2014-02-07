from askbot.models import User
from askbot.deps.django_authopenid.models import UserAssociation
from collections import defaultdict
from django.core.management.base import NoArgsCommand

def print_users(users):
    """prints data for the users"""
    for u in users:
        print '%d\t%s\t%s' % (u.id, u.username, u.email)

def print_associations(associations):
    for a in associations:
        u = a.user
        data = (a.id, a.openid_url, u.id, u.username, u.email)
        print 'a_id=%d\ta=%s\tu_id=%d\tu=%s\temail=%s' % data

def get_repeating_values(cls, field_name):
    values = cls.objects.values_list(field_name, flat=True)
    variants = defaultdict(int)
    repeats = set()
    for value in values:
        base = value.lower()
        variants[base] += 1
        if variants[base] > 1:
            repeats.add(base)
    return repeats

def print_count(items):
    num = len(items)
    if num == 0:
        print 'Not found'
    else:
        print '%d found' % num

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
        print_count(emails)

        print '\nLooking for users with duplicate username:'
        names = get_repeating_values(User, 'email')
        for name in names:
            users = User.objects.filter(username__iexact=name)
            print_users(users)
        print_count(names)

        print '\nLooking for users with duplicate login associations'
        logins = get_repeating_values(UserAssociation, 'openid_url')
        for login in logins:
            associations = UserAssociation.objects.filter(openid_url__iexact=login)
            print_associations(associations)
        print_count(names)
