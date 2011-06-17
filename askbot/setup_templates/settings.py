# Django settings for ASKBOT enabled project.
import os.path
import logging
import re
import sys
import askbot

#this is important to be able to import pre-packages askbot dependencies
sys.path.append(os.path.join(os.path.dirname(askbot.__file__), 'deps'))

#for logging
SITE_SRC_ROOT = os.path.dirname(__file__)
LOG_FILENAME = 'askbot.log'
logging.basicConfig(
    filename=os.path.join(SITE_SRC_ROOT, 'log', LOG_FILENAME),
    level=logging.CRITICAL,
    format='%(pathname)s TIME: %(asctime)s MSG: %(filename)s:%(funcName)s:%(lineno)d %(message)s',
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ()

#ADMINS and MANAGERS
ADMINS = (('Forum Admin', 'admin@askbot.org'),)
MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # only mysql is supported, more will be in the near future
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

CACHE_PREFIX = 'askbot-node2'
CACHE_TIMEOUT = 6000

#email server settings
SERVER_EMAIL = ''
DEFAULT_FROM_EMAIL = 'askbot@askbot.org'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_SUBJECT_PREFIX = '[ASKBOT] '
EMAIL_HOST='askbot.org'
EMAIL_PORT='25'
EMAIL_USE_TLS=False
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
LANGUAGE_CODE = 'en'
from languages import LANGUAGES, LANGUAGE_PROGRESS

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'askbot', 'upfiles')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://askbot.org/upfiles/'#set this to serve uploaded files correctly

PROJECT_ROOT = os.path.dirname(__file__)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

# Make up some unique string, and don't share it with anybody.
SECRET_KEY = '$oo^&_m&qwbib=(_4m_n*zn-d=g#s0he5fx9xonnym#8p6yigm'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'askbot.skins.loaders.load_template_source',
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    #below is askbot stuff for this tuple
    #'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    #'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.middleware.cache.UpdateCacheMiddleware',
    'askbot_site.middleware.JinjaDjangoLocaleUrlMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    #'django.middleware.sqlprint.SqlPrintingMiddleware',

    #below is askbot stuff for this tuple
    'askbot.middleware.anon_user.ConnectToSessionMessagesMiddleware',
    'askbot.middleware.pagesize.QuestionsPageSizeMiddleware',
    'askbot.middleware.cancel.CancelActionMiddleware',
    'askbot.deps.recaptcha_django.middleware.ReCaptchaMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'askbot.middleware.view_log.ViewLogMiddleware',
    'askbot.middleware.spaceless.SpacelessMiddleware',
)

CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_SECONDS = 3600


ROOT_URLCONF = os.path.basename(os.path.dirname(__file__)) + '.urls'

#UPLOAD SETTINGS
FILE_UPLOAD_TEMP_DIR = os.path.join(
                                os.path.dirname(__file__), 
                                'tmp'
                            ).replace('\\','/')

FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)
ASKBOT_ALLOWED_UPLOAD_FILE_TYPES = ('.doc','.jpg', '.jpeg', '.gif', '.bmp', '.png', '.tiff', '.pdf')
ASKBOT_MAX_UPLOAD_FILE_SIZE = 1024 * 1024 #result in bytes
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
ASKBOT_FILE_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'askbot', 'upfiles')


TEMPLATE_DIRS = (
    #specific to askbot
    os.path.join(os.path.dirname(__file__),'askbot','skins').replace('\\','/'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'askbot.context.application_settings',
    'django.core.context_processors.i18n',
    'askbot.user_messages.context_processors.user_messages',#must be before auth
    'django.core.context_processors.auth', #this is required for admin
    'django.core.context_processors.csrf',
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    #all of these are needed for the askbot
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    #'debug_toolbar',
    'askbot',
    'askbot.deps.django_authopenid',
    #'askbot.importers.stackexchange', #se loader
    'south',
    'askbot.deps.livesettings',
    'keyedcache',
    'rosetta',
    'localeurl',
    'robots',
    #'avatar',
    'djcelery',
    'djkombu',
    #'followit',
)

LOCALE_INDEPENDENT_PATHS = (
    re.compile(r'^/m/'),
    re.compile(r'^/rosetta'),
    re.compile(r'^/admin'),
    re.compile(r'^/cache'),
    re.compile(r'^/account/signin'),
    re.compile(r'^/account/delete_login_method'),
    re.compile(r'^/sitemap\.xml'),
    re.compile(r'^/doc'),
    re.compile(r'^/robots.txt'),
    re.compile(r'^/feeds/rss'),
    re.compile(r'^/upload'),
    re.compile(r'^/followit'),
)

#setup memcached for production use!
#see http://docs.djangoproject.com/en/1.1/topics/cache/ for details
#CACHE_BACKEND = 'memcached://74.208.164.82:11213/'
CACHE_BACKEND = 'locmem://'#memcached://74.208.164.82:11213/'
#If you use memcache you may want to uncomment the following line to enable memcached based sessions
#SESSION_ENGINE = 'django.contrib.sessions.backends.cache_db'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'askbot.deps.django_authopenid.backends.AuthBackend',
)

SESSION_ENGINE='django.contrib.sessions.backends.cached_db'

#logging settings
LOG_FILENAME = 'askbot.log'
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'log', LOG_FILENAME),
    level=logging.CRITICAL,
    format='%(pathname)s TIME: %(asctime)s MSG: %(filename)s:%(funcName)s:%(lineno)d %(message)s',
)

ASKBOT_URL = '' #no leading slash, default = '' empty string
_ = lambda v:v #fake translation function for the login url
LOGIN_URL = '/%s%s%s' % (ASKBOT_URL,'account/','signin/')
ASKBOT_UPLOADED_FILES_URL = '%s%s' % (ASKBOT_URL, 'upfiles/')

#Celery Settings
BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
CELERY_ALWAYS_EAGER = True

import djcelery
djcelery.setup_loader()


CSRF_COOKIE_NAME = 'askbot_csrf'
CSRF_COOKIE_DOMAIN = 'example.com'
