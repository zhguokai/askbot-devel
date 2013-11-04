from askbot.models import Message
from askbot.models import User
from askbot.models import ImportRun
from askbot.models import ImportedObjectInfo
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from django.db import transaction
from django.utils.encoding import smart_str
import os
import sys

def get_status_rank(status):
    """returns integer rank of user account status,
    the larger is the number the higher is the status"""
    if len(status) != 1:
        #default status - approved user
        status = 'a'
    try:
        return 'bswamd'.index(status)
    except ValueError:
        return 0

def get_safe_username(username):
    """get unique username similar to `username`
    to avoid the uniqueness clash"""
    existing_names = User.objects.filter(
                    username__istartswith=username
                ).values_list('username', flat=True)
    num = 1
    while True:
        new_name = username + str(num)
        if new_name in existing_names:
            num += 1
        else:
            return new_name

def get_deserialized_object(xml_soup):
    """returns deserialized django object for xml soup with one item"""
    item_xml = smart_str(xml_soup)
    #below call assumes a single item within
    return serializers.deserialize('xml', item_xml).next().object

def copy_string_parameter(from_obj, to_obj, param_name):
    from_par = getattr(from_obj, param_name)
    to_par = getattr(to_obj, param_name)
    if from_par.strip() == '' and to_par.strip() != '':
        setattr(to_obj, param_name, from_par)

def copy_bool_parameter(from_obj, to_obj, param_name, operator='or'):
    from_par = getattr(from_obj, param_name)
    to_par = getattr(to_obj, param_name)
    if operator == 'or':
        value = from_par or to_par
    elif operator == 'and':
        value = from_par and to_par
    else:
        raise ValueError('unsupported operator "%s"' % operator)
    setattr(to_obj, param_name, value)

def merge_words_parameter(from_obj, to_obj, param_name):
    from_words = getattr(from_obj, param_name).split()
    to_words = getattr(to_obj, param_name).split()
    value = ' '.join(set(from_words)|set(to_words))
    setattr(to_obj, param_name, value)

def copy_numeric_parameter(from_obj, to_obj, param_name, operator='max'):
    from_par = getattr(from_obj, param_name)
    to_par = getattr(to_obj, param_name)
    if operator == 'max':
        value = max(from_par, to_par)
    elif operator == 'min':
        value = min(from_par, to_par)
    elif operator == 'sum':
        value =  from_par + to_par
    else:
        raise ValueError('unsupported operator "%s"' % operator)
    setattr(to_obj, param_name, value)

class Command(BaseCommand):
    help = 'Adds XML askbot data produced by the "dumpdata" command'

    def handle(self, *args, **kwargs):
        self.setup_run()
        self.read_xml_file(args[0])
        self.remember_message_ids()
        self.import_users()
        self.import_user_logins()
        self.import_questions()
        self.import_answers()
        self.import_comments()
        self.import_badges()
        self.import_votes()
        self.delete_new_messages()

    def setup_run(self):
        """remembers the run information, 
        for the logging purposes
        """
        command = ' '.join(sys.argv)
        run = ImportRun.objects.create(command=command)
        self.run = run

    def read_xml_file(self, filename):
        if not os.path.isfile(filename):
            raise CommandError('File %s does not exist') % filename
        xml = open(filename, 'r').read() 
        self.soup = BeautifulSoup(xml, ['lxml', 'xml'])

    def remember_message_ids(self):
        self.message_ids = list(Message.objects.values_list('id', flat=True))

    def log_action(self, from_object, to_object, info=None):
        info = ImportedObjectInfo()
        info.old_id = from_object.id
        info.new_id = to_object.id
        info.model = str(to_object._meta)
        info.run = self.run
        info.extra_info = info or dict()
        info.save()

    def get_objects_for_model(self, model_name):
        """returns iterator of objects from the django
        xml dump by name"""
        object_soup = self.soup.find_all('object', {'model': model_name})
        for datum in object_soup:
            yield get_deserialized_object(datum)

    def import_users(self):
        model_path = str(User._meta)
        dupes = 0
        for from_user in self.get_objects_for_model('auth.user'):
            log_info = dict()
            log_info['notify_user'] = list()
            try:
                to_user = User.objects.get(email=from_user.email)
                dupes += 1
            except User.DoesNotExist:
                username = get_safe_username(from_user.username)
                if username != from_user.username:
                    template = 'Your user name was changed from %s to %s'
                    log_info['notify_user'].append(template % (from_user.username, username))
                to_user = User.objects.create_user(username, from_user.email)

            #copy the data
            if from_user.username != to_user.username:
                names = (from_user.username, to_user.username)
                log_info['notify_user'].append('Your user name has changed from %s to %s' % names)

            copy_string_parameter(from_user, to_user, 'first_name')
            copy_string_parameter(from_user, to_user, 'last_name')
            copy_string_parameter(from_user, to_user, 'real_name')
            copy_string_parameter(from_user, to_user, 'website')
            copy_string_parameter(from_user, to_user, 'location')

            to_user.country = from_user.country

            copy_string_parameter(from_user, to_user, 'about')
            copy_string_parameter(from_user, to_user, 'email_signature')
            copy_string_parameter(from_user, to_user, 'twitter_access_token')
            copy_string_parameter(from_user, to_user, 'twitter_handle')

            merge_words_parameter(from_user, to_user, 'interesting_tags')
            merge_words_parameter(from_user, to_user, 'ignored_tags')
            merge_words_parameter(from_user, to_user, 'subscribed_tags')
            merge_words_parameter(from_user, to_user, 'languages')

            if to_user.password == '!' and from_user.password != '!':
                to_user.password = from_user.password
            copy_bool_parameter(from_user, to_user, 'is_staff')
            copy_bool_parameter(from_user, to_user, 'is_active')
            copy_bool_parameter(from_user, to_user, 'is_superuser')
            copy_bool_parameter(from_user, to_user, 'is_fake', operator='and')
            copy_bool_parameter(from_user, to_user, 'email_isvalid', operator='and')
            copy_bool_parameter(from_user, to_user, 'show_country')
            copy_bool_parameter(from_user, to_user, 'show_marked_tags')

            copy_numeric_parameter(from_user, to_user, 'last_login')
            copy_numeric_parameter(from_user, to_user, 'last_seen')
            copy_numeric_parameter(from_user, to_user, 'date_joined', operator='min')
            copy_numeric_parameter(from_user, to_user, 'email_tag_filter_strategy')
            copy_numeric_parameter(from_user, to_user, 'display_tag_filter_strategy')
            copy_numeric_parameter(
                from_user,
                to_user, 
                'consecutive_days_visit_count',
                operator='sum'
            )
            copy_numeric_parameter(from_user, to_user, 'social_sharing_mode')

            #position of character in this string == rank of status
            if get_status_rank(from_user.status) > get_status_rank(to_user.status):
                to_user.status = from_user.status

            """
            <field type="CharField" name="email_key"><None></None></field>
            <field type="PositiveIntegerField" name="reputation">1</field>
            <field type="SmallIntegerField" name="gold">0</field>
            <field type="SmallIntegerField" name="silver">0</field>
            <field type="SmallIntegerField" name="bronze">0</field>
            <field type="IntegerField" name="new_response_count">0</field>
            <field type="IntegerField" name="seen_response_count">0</field>
            """
            self.log_action(from_user, to_user, log_info)

    @transaction.commit_manually
    def import_user_logins(self):
        #logins_soup = self.soup.find_all('object', {'model': 'django_authopenid.userassociation'})
        #for login_info in self.get_objects_for_model('django_authopenid.userassociation'):
        #for login_
        for association in self.get_objects_for_model('django_authopenid.userassociation'):
            #where possible, we should copy the login, but respecting the
            #uniqueness constraints: ('user','provider_name'), ('openid_url', 'provider_name')
            #1) get new user by old id
            user_info = ImportedObjectInfo.objects.get(
                                            model='auth.user',
                                            old_id=association.user_id,
                                            run=self.run
                                        )
            user = User.objects.get(id=user_info.new_id)
            try:
                association.user = user
                association.save()
                transaction.commit()
                print 'yeah!!!'
            except:
                transaction.rollback()

    def import_questions(self):
        pass

    def import_answers(self):
        pass

    def import_comments(self):
        pass

    def import_badges(self):
        pass

    def import_votes(self):
        pass

    def delete_new_messages(self):
        Message.objects.exclude(id__in=self.message_ids).delete()
