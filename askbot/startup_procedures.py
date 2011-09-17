"""tests to be performed
in the beginning of models/__init__.py

the purpose of this module is to validate deployment of askbot

question: why not run these from askbot/__init__.py?

the main function is run_startup_tests
"""
import sys
from import_utils import import_module
from django.db import transaction
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from askbot.models import badges
from askbot.utils.functions import enumerate_string_list

PREAMBLE = """\n
************************
*                      *
*   Askbot self-test   *
*                      *
************************\n
"""

FOOTER = """\n
If necessary, type ^C (Ctrl-C) to stop the program, then resolve the issues.
"""

class AskbotConfigError(ImproperlyConfigured):
    """Prints an error with a preamble and possibly a footer"""
    def __init__(self, error_message):
        msg = PREAMBLE + error_message
        if sys.__stdin__.isatty():
            #print footer only when askbot is run from the shell
            msg += FOOTER
        super(AskbotConfigError, self).__init__(msg)

def maybe_report_errors(error_messages, header = None, footer = None):
    """if there is one or more error messages,
    raise ``class:AskbotConfigError`` with the human readable
    contents of the message
    * ``header`` - text to show above messages
    * ``footer`` - text to show below messages
    """
    if len(error_messages) == 0: return
    if len(error_messages) > 1:
        error_messages = enumerate_string_list(error_messages)

    message = ''
    if header: message += header + '\n'
    message += 'Please attend to the following:\n\n'
    message += '\n\n'.join(error_messages)
    if footer: message += '\n\n' + footer
    raise AskbotConfigError(message)

def askbot_warning(line):
    """prints a warning with the nice header, but does not quit"""
    print >> sys.stderr, PREAMBLE + '\n' + line

def format_as_text_tuple_entries(items):
    """prints out as entries or tuple containing strings
    ready for copy-pasting into say django settings file"""
    return "    '%s'," % "',\n    '".join(items)

#todo:
#
# *validate emails in settings.py
def test_askbot_url():
    """Tests the ASKBOT_URL setting for the 
    well-formedness and raises the ImproperlyConfigured
    exception, if the setting is not good.
    """
    url = django_settings.ASKBOT_URL
    if url != '':

        if isinstance(url, str) or isinstance(url, unicode):
            pass
        else:
            msg = 'setting ASKBOT_URL must be of string or unicode type'
            raise AskbotConfigError(msg)

        if url == '/':
            msg = 'value "/" for ASKBOT_URL is invalid. '+ \
                'Please, either make ASKBOT_URL an empty string ' + \
                'or a non-empty path, ending with "/" but not ' + \
                'starting with "/", for example: "forum/"'
            raise AskbotConfigError(msg)
        else:
            try:
                assert(url.endswith('/'))
            except AssertionError:
                msg = 'if ASKBOT_URL setting is not empty, ' + \
                        'it must end with /'
                raise AskbotConfigError(msg)
            try:
                assert(not url.startswith('/'))
            except AssertionError:
                msg = 'if ASKBOT_URL setting is not empty, ' + \
                        'it must not start with /'

def test_middleware():
    """Checks that all required middleware classes are
    installed in the django settings.py file. If that is not the
    case - raises an AskbotConfigErrorexception.
    """
    required_middleware = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'askbot.middleware.anon_user.ConnectToSessionMessagesMiddleware',
        'askbot.middleware.pagesize.QuestionsPageSizeMiddleware',
        'askbot.middleware.cancel.CancelActionMiddleware',
        #'askbot.deps.recaptcha_django.middleware.ReCaptchaMiddleware',
        'django.middleware.transaction.TransactionMiddleware',
        'askbot.middleware.view_log.ViewLogMiddleware',
    )
    if 'debug_toolbar' in django_settings.INSTALLED_APPS:
        required_middleware += (
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        )

    installed_middleware_set = set(django_settings.MIDDLEWARE_CLASSES)
    missing_middleware_set = set(required_middleware) - installed_middleware_set

    if missing_middleware_set:
        error_message = """\n\nPlease add the following middleware (listed after this message)
to the MIDDLEWARE_CLASSES variable in your site settings.py file. 
The order the middleware records may be important, please take a look at the example in 
https://github.com/ASKBOT/askbot-devel/blob/master/askbot/setup_templates/settings.py:\n\n"""
        middleware_text = format_as_text_tuple_entries(missing_middleware_set)
        raise AskbotConfigError(error_message + middleware_text)


    #middleware that was used in the past an now removed
    canceled_middleware = (
        'askbot.deps.recaptcha_django.middleware.ReCaptchaMiddleware',
    )
    #'debug_toolbar.middleware.DebugToolbarMiddleware',

    remove_middleware_set = set(canceled_middleware) \
                                & installed_middleware_set
    if remove_middleware_set:
        error_message = """\n\nPlease remove the following middleware entries from
the list of MIDDLEWARE_CLASSES in your settings.py - these are not used any more:\n\n"""
        middleware_text = format_as_text_tuple_entries(remove_middleware_set)
        raise AskbotConfigError(error_message + middleware_text)

            

def test_i18n():
    """askbot requires use of USE_I18N setting"""
    if getattr(django_settings, 'USE_I18N', False) == False:
        raise AskbotConfigError(
            'Please set USE_I18N = True in settings.py and '
            'set the LANGUAGE_CODE parameter correctly '
            'it is very important for askbot.'
        )

def try_import(module_name, pypi_package_name):
    """tries importing a module and advises to install 
    A corresponding Python package in the case import fails"""
    try:
        import_module(module_name)
    except ImportError, error:
        message = unicode(error) + ' run\npip install %s' % pypi_package_name
        message += '\nTo install all the dependencies at once, type:'
        message += '\npip install -r askbot_requirements.txt\n'
        raise AskbotConfigError(message)

def test_modules():
    """tests presence of required modules
    when any of the modules are absent, prints
    a recommendation on how to install a module
    """
    try_import('recaptcha_works', 'django-recaptcha-works')
    try_import('wordpress_xmlrpc', 'python-wordpress-xmlrpc')
    try_import('multi_registry', 'python-multi-registry')
    try_import('django_extra_form_fields', 'django-extra-form-fields')
    try_import('import_utils', 'import-utils')
    try_import('django_authenticator', 'django-authenticator')

def test_template_loaders():
    """reports recommendations about TEMPLATE_LOADERS
    setting, when appropriate"""
    loader_errors = list()
    if 'askbot.skins.loaders.load_template_source' in \
        django_settings.TEMPLATE_LOADERS:        
        msg = """remove entry 'askbot.skins.loaders.load_template_source',
from the TEMPLATE_LOADERS list in settings.py - 
this loader is no longer in use"""
        loader_errors.append(msg)

    if 'askbot.skins.loaders.Loader' not in django_settings.TEMPLATE_LOADERS:
        msg = """add entry 'askbot.skins.loaders.Loader', to TEMPLATE_LOADERS
in your settings.py"""
        loader_errors.append(msg)

    maybe_report_errors(
        loader_errors,
        header = 'There are some problems with TEMPLATE_LOADERS in your settings.py file.'
    )

def test_urlconf():
    """tests url configuration"""
    return#does not work for some reason...
    if getattr(django_settings, 'DISABLE_ASKBOT_ERROR_VIEWS', True):
        import urls
        handler500 = getattr(urls, 'handler500', None)
        handler404 = getattr(urls, 'handler404', None)
        url_errors = list()
        message_template = "add line:\n%s = '%s'\nto your urls.py file"
        handler500_path = 'askbot.views.meta.server_error'
        if handler500 != handler500_path:
            url_errors.append(message_template % ('handler500', handler500_path))
        handler404_path = 'askbot.views.meta.page_not_found'
        if handler404 != handler404_path:
            url_errors.append(message_template % ('handler404', handler404_path))

        footer = """If you want to use custom url handlers,
please add them manually to your urls.py file
and add line:
DISABLE_ASKBOT_ERROR_VIEWS = True
to your settings.py file"""
        maybe_report_errors(
            url_errors,
            header = 'There are some problems with your urls.py file',
            footer = footer
        )

def explain_replacement_of_django_authopenid():
    """.. versionadded: 0.7.23"""
    raise AskbotConfigError(
        """ATTENTION! Askbot now uses application "django_authenticator" 
in place of "askbot.deps.django_authopenid, therefore you will 
need to do the following :
1) install "django_authenticator" by typing:

    pip install -r askbot_requirements.txt

2) Edit settings.py file.

(a) In INSTALLED_APPS replace

    'askbot.deps.django_authopenid',
with
    'django_authenticator',

(b) in AUTHENTICATION_BACKENDS replace

    'askbot.deps.django_authopenid.backends.AuthBackend',
with
    'django_authenticator.backends.AuthBackend',"""
    )

def test_misc_settings():
    """tests various settings"""
    if 'askbot.deps.django_authopenid' in django_settings.INSTALLED_APPS or \
       'askbot.deps.django_authopenid.backends.AuthBackend' in \
       django_settings.AUTHENTICATION_BACKENDS:
        explain_replacement_of_django_authopenid()
    if 'django_authenticator' in django_settings.INSTALLED_APPS:
        mod_path = getattr(django_settings, 'EXTRA_SETTINGS_MODULE', '')
        if mod_path != 'askbot.conf.settings':
            raise AskbotConfigError(
                'If you are using django_authenticator, '
                'please also add the following line to your settings: '
            )
         
    if django_settings.LOGIN_REDIRECT_URL != '/' + django_settings.ASKBOT_URL:
        print """Warning:
For askbot, add line to settings.py:

LOGIN_REDIRECT_URL = '/' + ASKBOT_URL

This warning can be ignored, if you indeed need to
customize the LOGIN_REDIRECT_URL setting
"""

def test_postgres():
    """Checks for the postgres buggy driver, version 2.4.2"""
    if hasattr(django_settings, 'DATABASE_ENGINE'):
        if django_settings.DATABASE_ENGINE in ('postgresql_psycopg2',):
            try:
                import psycopg2
                version = psycopg2.__version__.split(' ')[0].split('.')
                if version == ['2', '4', '2']:
                    raise ImproperlyConfigured(
                        'Please install psycopg2 version 2.4.1,\n version 2.4.2 has a bug'
                    )
                elif version > ['2', '4', '2']:
                    pass #don't know what to do
                else:
                    pass #everythin is ok
            except ImportError:
                #Using mysql not a problem
                pass
        else:
            pass #using other thing than postgres
    else:
        pass #TODO: test new django dictionary databases

def test_encoding():
    """prints warning if encoding error is not UTF-8"""
    if hasattr(sys.stdout, 'encoding'):
        if sys.stdout.encoding != 'UTF-8':
            askbot_warning(
                'Your output encoding is not UTF-8, there may be '
                'issues with the software when anything is printed '
                'to the terminal or log files'
            )

def run_startup_tests():
    """function that runs
    all startup tests, mainly checking settings config so far
    """

    #todo: refactor this when another test arrives
    test_encoding()
    test_modules()
    test_askbot_url()
    test_i18n()
    test_postgres()
    test_middleware()
    test_template_loaders()
    test_misc_settings()
    try:
        #unfortunately cannot test urls
        #at the startup time. a command askbot_selftest will access these
        test_urlconf()
    except ImportError:
        pass

@transaction.commit_manually
def run():
    """runs all the startup procedures"""
    run_startup_tests()
    try:
        badges.init_badges()
        transaction.commit()
    except Exception, error:
        print error
        transaction.rollback()
