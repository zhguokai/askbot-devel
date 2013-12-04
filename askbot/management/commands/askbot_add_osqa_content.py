from askbot.management.commands.base import BaseImportXMLCommand
from askbot.models import User

class Command(BaseImportXMLCommand):
    help = 'Adds XML OSQA data produced by the "dumpdata" command'

    def handle_import(self):

        #site settings
        #forum.keyvalue

        #auth.user
        #forum.user
        self.import_users()

        #model="forum.tag"

        #model="forum.action"
        #model="forum.actionrepute"
        #model="forum.answer"
        #model="forum.award"
        #model="forum.badge"
        #model="forum.comment"

        #model="forum.noderevision"
        #model="forum.nodestate"

        #model="forum.question"
        #model="forum.questionsubscription"
        #model="forum.subscriptionsettings"
        #model="forum.userproperty"
        #model="forum.validationhash"
        #model="forum.vote"
        
        #forum.authkeyuserassociation
        #self.import_user_logins()
        #self.import_tags()
        #self.import_marked_tags()

        #self.import_threads()
        #self.apply_groups_to_threads()

        #model="askbot.posttogroup">
        #self.import_posts('question', save_redirects=True)
        #self.import_posts('answer')
        #self.import_posts('comment')
        #self.import_post_revisions()
        #self.apply_groups_to_posts()
        #self.apply_question_followers()
        #self.import_votes()

        #self.import_badges()
        #self.import_badge_awards()

    def import_users(self):
        """import OSQA users to Askbot users"""
        #in OSQA user profile is splite in two models
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
            user.reputation += profile.reputation - 1
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
