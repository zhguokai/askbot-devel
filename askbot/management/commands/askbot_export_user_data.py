"""Exports data for a user with given ID"""
import os
import re
import shutil
import tempfile
from optparse import make_option
from django.conf import settings as django_settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson as json
from askbot.models import User
from askbot.utils.html import site_url
from askbot.utils.functions import list_directory_files, zipzip

class Command(BaseCommand):
    """Exports data for a user given his or her ID"""

    option_list = BaseCommand.option_list + (
        make_option('--user-id',
                    action='store',
                    type='int',
                    dest='user_id',
                    default=None,
                    help='ID of the user whose data we will export'),
        make_option('--file',
                    action='store',
                    dest='file_name',
                    type='str',
                    default=None,
                    help='Path to the output file, absolute or relative to CWD'))

    def handle(self, *args, **options):
        """Does the job of the command"""
        uid, file_name = self.get_params(options)

        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist: #pylint: disable=no-member
            raise CommandError('User with id {} does not exist'.format(uid))

        data = {'about': user.about,
                'date_of_birth': user.date_of_birth,
                'username': user.username,
                'profile_url': site_url(user.get_absolute_url()),
                'email': user.email}

        question_data = self.get_question_data(user)
        data['questions'] = question_data.values()

        answer_data = self.get_post_data(user, 'answer')
        data['answers'] = answer_data.values()

        comment_data = self.get_post_data(user, 'comment')
        data['comments'] = comment_data.values()

        upfiles = self.get_user_upfiles(user)

        temp_dir = tempfile.mkdtemp()
        dir_path = self.backup_upfiles_and_avatar(upfiles, user, temp_dir)

        self.save_json_file(data, temp_dir)
        self.zip_tempdir(temp_dir, options['file_name'])

        shutil.rmtree(temp_dir)

    @classmethod
    def get_params(cls, options):
        """Returns cleaned parameters or raises `CommandErrror`"""
        uid = options['user_id']
        file_name = options['file_name']
        if not (uid or file_name):
            raise CommandError('Parameters --user-id and --file are required')
        if not uid:
            raise CommandError('Parameter --user-id is required')
        if not file_name:
            raise CommandError('Parameter --file is required')

        if not file_name.endswith('.zip'):
            file_name += '.zip'

        return uid, file_name

    @classmethod
    def save_json_file(cls, data, temp_dir):
        """Saves data in json form in the temporary directory"""
        json_file_path = os.path.join(temp_dir, 'data.json')
        file_obj = open(json_file_path, 'w')
        file_obj.write(json.dumps(data, indent=2))
        file_obj.close()

    @classmethod
    def zip_tempdir(cls, temp_dir, file_name):
        """Zip contents of the temp directory into the desired
        target file"""
        if os.path.exists(file_name):
            raise CommandError('File {} already exists'.format(file_name))
        zip_path = os.path.abspath(file_name)

        file_paths = list_directory_files(temp_dir)
        zipzip(zip_path, *file_paths, ignore_subpath=temp_dir)

    @classmethod
    def backup_upfiles_and_avatar(cls, upfiles, user, temp_dir):
        """Copies the uploaded files and the avatar to the
        temporary directory"""
        pass

    @classmethod
    def extract_upfile_paths_from_text(cls, text):
        """Returns strings resembling urls to uploaded files"""
        #todo: unit test this
        upfiles = set()
        start = django_settings.MEDIA_URL
        # '(/upfiles/[^)\s\'\"]+)'
        non_space = '[^)\\s\'\"]+'
        pattern = '(' + start + non_space + ')'
        upfile_re = re.compile(pattern)
        ptr = re.compile(pattern)
        upfiles = set()
        for match in ptr.finditer(text):
            upfiles |= set(match.groups())
        return upfiles

    @classmethod
    def upfile_is_on_disk(cls, upfile):
        """`True` if file is found relative to the
        `settings.MEDIA_ROOT` directory"""
        media_root = django_settings.MEDIA_ROOT
        media_url = django_settings.MEDIA_URL
        file_name = upfile[len(media_url):]
        file_path = os.path.join(media_root, file_name)
        return os.path.isfile(file_path)

    @classmethod
    def get_user_upfiles(cls, user):
        """Returns set of upfiles of all user posts, and only those
        that can be found in the upfiles directory"""
        post_types = ('question', 'answer', 'comment')
        posts = user.posts.filter(post_type__in=post_types)
        have_thread = [post for post in posts if post.thread_id]
        exportable = list()
        for post in have_thread:
            if post.is_question() or post.parent_id:
                exportable.append(post)

        upfiles = set()
        for post in exportable:
            upfiles |= cls.extract_upfile_paths_from_text(post.text) #pylint: disable=no-member

        confirmed = [upfile for upfile in upfiles if cls.upfile_is_on_disk(upfile)] #pylint: disable=no-member
        return confirmed

    @classmethod
    def get_post_upfiles(cls, post):
        """Returns dictionary valued with uploaded file paths
        relative to the upfiles directory, extracted from
        the post.text and present on the file system.
        Keys are posts."""
        paths = cls.extract_upfile_paths_from_text(post.text)

    @classmethod
    def get_post_data(cls, user, post_type):
        """Returns a dictionary valued with with question data,
        keyed by question objects."""
        posts = user.posts.filter(post_type=post_type)

        # prune threadless posts and parentless
        good_posts = list()
        have_threads = [post for post in posts if post.thread_id]
        if post_type == 'question':
            exportable = have_threads
        else:
            exportable = [post for post in posts if post.parent_id]

        # collect data per post:
        data = dict()
        for post in exportable:
            datum = {'text': post.text,
                     'added_at': str(post.added_at),
                     'last_edited_at': str(post.last_edited_at),
                     'url': site_url(post.get_absolute_url())}
            data[post] = datum

        return data

    @classmethod
    def get_question_data(cls, user):
        """Returns the same as the `get_post_data` method,
        but in addition fills in question title and the tags"""
        post_data = cls.get_post_data(user, 'question')
        for question, datum in post_data.items():
            datum['title'] = question.thread.title
            datum['tags'] = question.thread.tagnames

        return post_data
