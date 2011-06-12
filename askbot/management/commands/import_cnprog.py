"""importer from cnprog, please note, that you need an exporter in the first place
to use this command.
If you are interested to use it - please ask Evgeny <evgeny.fadeev@gmail.com>
"""
import os
import sys
import tarfile
import tempfile
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from lxml import etree
from askbot import models
from askbot.utils import console

def get_val(elem, field_name):
    field = elem.find('field[@name="%s"]' % field_name)
    field_type = field.attrib['type']
    raw_val = field.text
    if field_type == 'BooleanField':
        return bool(raw_val)
    elif field_type.endswith('IntegerField'):
        return int(raw_val)
    elif field_type == 'DateTimeField':
        if raw_val:
            return datetime.strptime(raw_val, '%Y-%m-%d %H:%M:%S')
        else:
            return None
    elif field_type == 'DateField':
        if raw_val:
            return datetime.strptime(raw_val, '%Y-%m-%d')
        else:
            return None
    elif field_type in ('CharField', 'TextField'):
        if raw_val:
            return raw_val
        else:
            return ''
    else:
        return raw_val

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if len(args) != 1:
            raise CommandError('please provide path to tarred and gzipped cnprog dump')

        self.tar = tarfile.open(args[0], 'r:gz')
        
        sys.stdout.write("Importing user accounts: ")
        self.import_users()
        #self.import_openid_associations()
        #self.import_email_settings()

        #self.import_question_edits()
        #self.import_answer_edits()

        #self.import_question_data()
        #self.import_answer_data()

        #self.import_comments()

        #self.import_question_views()
        #self.import_favorite_questions()
        #self.import_marked_tags()

        #self.import_votes()

    def get_file(self, file_name):
        first_item = self.tar.getnames()[0]
        file_path = file_name
        if not first_item.endswith('.xml'):
            file_path = os.path.join(first_item, file_path)
            
        file_info = self.tar.getmember(file_path)
        xml_file = self.tar.extractfile(file_info)
        return etree.parse(xml_file)

    @transaction.commit_manually
    def import_users(self):
        xml = self.get_file('users.xml')
        added_users = 0
        for user in xml.findall('object'):
            ab_user = models.User(
                about = get_val(user, 'about'),
                date_of_birth = get_val(user, 'date_of_birth'),
                email = get_val(user, 'email'),
                email_isvalid = get_val(user, 'email_isvalid'),
                email_key = get_val(user, 'email_key'),
                gravatar = get_val(user, 'gravatar'),
                gold = get_val(user, 'gold'),
                last_seen = get_val(user, 'last_seen'),
                location = get_val(user, 'location'),
                password = get_val(user, 'password'),
                real_name = get_val(user, 'real_name'),
                username = get_val(user, 'username'),
                website = get_val(user, 'website'),
                questions_per_page = get_val(user, 'questions_per_page')
            )
            ab_user.save()
            added_users += 1
            console.print_action(ab_user.username)
            transaction.commit()
        console.print_action('%d users added' % added_users, nowipe = True)
        transaction.commit()
