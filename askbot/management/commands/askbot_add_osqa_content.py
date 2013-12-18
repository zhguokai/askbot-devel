from askbot.deps.django_authopenid.models import UserAssociation
from askbot.management.commands.base import BaseImportXMLCommand
from askbot.models import Award
from askbot.models import BadgeData
from askbot.models import Tag
from askbot.models import User
from askbot.utils.slug import slugify_camelcase
from bs4 import BeautifulSoup
from datetime import datetime
from django.utils import translation
from django.conf import settings as django_settings

def decode_datetime(data):
    """Decodes formats:
    * '2013-10-25 09:46:34'
    * '2013-10-25'
    """
    if data:
        try:
            return datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.strptime(data, '%Y-%m-%d')
    return None

class DataObject(object):
    def __init__(self, soup):
        """Initializes object based on the values passed
        via BeautifulSoup instance for that object"""
        self.soup = soup
        self.data = dict()

    def decode_typed_value(self, field):
        field_type = field['type']
        value = field.text.strip()
        if field_type == 'BooleanField':
            if value == 'False':
                return False
            else:
                return True
        elif field_type in ('CharField', 'TextField'):
            return value
        elif 'Integer' in field_type:
            return int(value)
        elif field_type in ('DateField', 'DateTimeField'):
            return decode_datetime(value)
        else:
            raise ValueError('unknown field type: %s' % field_type)

    def decode_rel_value(self, field):
        rel_type = field['rel']
        if rel_type in ('ManyToOneRel', 'OneToOneRel'):
            return int(field.text)
        elif rel_type == 'ManyToManyRel':
            items = field.find_all('object')
            return [item['pk'] for item in items]
        else:
            raise ValueError('unknown relation type %s' % rel_type)

    def decode_value(self, key):
        """
        type="DateField">
        type="DateTimeField">
        """
        if key in ('pk', 'id'):
            return self.soup['pk']
        field = self.soup.find('field', attrs={'name': key})
        if field is None:
            raise ValueError('could not find field %s' % key)
        if field.get('type') != None:
            return self.decode_typed_value(field)
        elif field.get('rel') != None:
            return self.decode_rel_value(field)
        else:
            raise ValueError('unknown field class %s - neither data nor relation')
        
        
    def __getattr__(self, key):
        """Returns value of property, if decoded
        or decodes the property first from the bs4 soup"""
        if key not in self.data:
            value = self.decode_value(key)
            self.data[key] = value
        return self.data[key]


class Command(BaseImportXMLCommand):
    args = '<xml file>'
    help = 'Adds XML OSQA data produced by the "dumpdata" command'

    def handle(self, *args, **options):
        translation.activate(django_settings.LANGUAGE_CODE)

        self.setup_run()

        dump_file_name = args[0]
        xml = open(dump_file_name, 'r').read() 
        self.soup = BeautifulSoup(xml, ['lxml', 'xml'])

        #site settings
        #forum.keyvalue
        self.import_users()
        self.import_user_logins()
        #model="forum.subscriptionsettings"
        #this model has no correspondence in Askbot

        #model="forum.actionrepute"
        #model="forum.award"

        #model="forum.noderevision"
        #model="forum.nodestate"

        #model="forum.question"
        #model="forum.questionsubscription"
        #model="forum.userproperty"
        #model="forum.validationhash"
        #model="forum.vote"
        
        #model="forum.tag"
        self.import_tags()
        #self.import_marked_tags()

        #self.import_threads()
        #self.apply_groups_to_threads()

        #forum.question
        #self.import_posts('question', save_redirects=True)
        #self.import_posts('answer')
        #self.import_posts('comment')
        #self.import_post_revisions()
        #self.apply_groups_to_posts()
        #self.apply_question_followers()
        #self.import_votes()

        self.import_badges()
        #self.import_badge_awards()

    def get_objects_for_model(self, model):
        objects_soup = self.soup.find_all(attrs={'model': model})
        for item_soup in objects_soup:
            yield DataObject(item_soup)

    def import_users(self):
        """import OSQA users to Askbot users"""
        #in OSQA user profile is split in two models
        #auth.user
        #forum.user

        for from_user in self.get_objects_for_model('auth.user'):
            try:
                to_user = User.objects.get(email=from_user.email)
            except User.DoesNotExist:
                username = self.get_safe_username(from_user.username)
                to_user = User.objects.create_user(username, from_user.email)

            self.copy_string_parameter(from_user, to_user, 'first_name')
            self.copy_string_parameter(from_user, to_user, 'last_name')
            self.copy_string_parameter(from_user, to_user, 'password')
            self.copy_bool_parameter(from_user, to_user, 'is_staff')
            self.copy_bool_parameter(from_user, to_user, 'is_active')
            self.copy_bool_parameter(from_user, to_user, 'is_superuser')
            self.copy_numeric_parameter(from_user, to_user, 'last_login', operator='max')
            self.copy_numeric_parameter(from_user, to_user, 'date_joined', operator='min')
            to_user.save()

            self.log_action(from_user, to_user)

        for profile in self.get_objects_for_model('forum.user'):
            user = self.get_imported_object_by_old_id(User, profile.id)
            self.copy_bool_parameter(profile, user, 'email_isvalid')
            user.reputation = max(user.reputation + profile.reputation - 1, 1)
            user.gold += profile.gold
            user.silver += profile.silver
            user.bronze += profile.bronze
            self.copy_string_parameter(profile, user, 'real_name')
            self.copy_numeric_parameter(profile, user, 'last_seen', operator='max')
            self.copy_string_parameter(profile, user, 'website')
            self.copy_string_parameter(profile, user, 'location')
            self.copy_numeric_parameter(profile, user, 'date_of_birth')
            self.copy_string_parameter(profile, user, 'about')
            user.save()

    def import_user_logins(self):
        """import user's login methods from OSQA to Askbot"""
        for user_login in self.get_objects_for_model('forum.authkeyuserassociation'):
            assoc = UserAssociation()
            assoc.openid_url = user_login.key
            assoc.user =  self.get_imported_object_by_old_id(User, user_login.user)
            assoc.provider_name = user_login.provider
            assoc.last_used_timestamp = user_login.added_at
            assoc.save()

    def import_tags(self):
        """imports OSQA tags to Askbot tags"""
        """
        <object model="forum.tag" pk="2">
            <field name="name" type="CharField">
            pro
            </field>
            <field name="created_by" rel="ManyToOneRel" to="forum.user">
            1
            </field>
            <field name="created_at" type="DateTimeField">
            2012-06-09 18:34:13
            </field>
            <field name="used_count" type="PositiveIntegerField">
            259
            </field>
        </object>
        """
        for osqa_tag in self.get_objects_for_model('forum.tag'):
            tag = Tag()
            tag.name = osqa_tag.name
            tag.created_by = self.get_imported_object_by_old_id(User, osqa_tag.created_by)
            tag.used_count = osqa_tag.used_count
            tag.save()

    def import_badges(self):
        """remembers relation of OSQA badges with Askbot badges"""
        #model="forum.badge"
        for osqa_badge in self.get_objects_for_model('forum.badge'):
            badge_slug = slugify_camelcase(osqa_badge.cls)
            try:
                askbot_badge = BadgeData.objects.get(slug=badge_slug)
            except BadgeData.DoesNotExist:
                print 'Could not find an equivalent to badge %s in Askbot' % osqa_badge.cls
                continue
            self.log_action(osqa_badge, askbot_badge)
        """
        <object model="forum.badge" pk="1">
            <field name="type" type="SmallIntegerField">
                3
            </field>
            <field name="cls" type="CharField">
                PopularQuestion
            </field>
            <field name="awarded_count" type="PositiveIntegerField">
                0
            </field>
        </object>
        """
        """
        slug = models.SlugField(max_length=50, unique=True)
        awarded_count = models.PositiveIntegerField(default=0)
        awarded_to = models.ManyToManyField(
                        User, through='Award', related_name='badges'
                    )
        """

    def import_badge_awards(self):
        """Makes sure that users are re-awarded all previously
        awarded OSQA badges"""
        for osqa_award in self.get_objects_for_model('forum.award'):
            user = self.get_imported_object_by_old_id(User, osqa_award.user)
            badge = self.get_imported_object_by_old_id(BadgeData, osqa_award.badge)
            if badge is None:
                continue
            print 'awarding badge %s' % badge.slug
            #if multiple or user does not have this badge, then award
            if badge.is_multiple() or (not user.has_badge(badge)):
                award = Award()
                award.badge = badge
                award.user = user
                award.notified = True
                #todo: here we need to map to the node object
                #content_type = self.get_content_type_by_old_id(award.content_type_id)
                #obj_class = content_type.model_class()
                #award.object_id = self.get_imported_object_id_by_old_id(obj_class, award.object_id)
                #award.content_type = content_type
                award.save()
            """
            <object model="forum.award" pk="1">
                <field name="user" rel="ManyToOneRel" to="forum.user">
                    1
                </field>
                <field name="badge" rel="ManyToOneRel" to="forum.badge">
                    32
                </field>
                <field name="node" rel="ManyToOneRel" to="forum.node">
                    <None/>
                </field>
                <field name="awarded_at" type="DateTimeField">
                    2012-06-08 17:49:15
                </field>
                <field name="trigger" rel="ManyToOneRel" to="forum.action">
                    4
                </field>
                <field name="action" rel="OneToOneRel" to="forum.action">
                    6
                </field>
            </object>
            """
