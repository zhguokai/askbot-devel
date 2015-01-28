"""
Definition of a Singleton wrapper class for askbot.deps.livesettings
with interface similar to django.conf.settings
that is each setting has unique key and is accessible
via dotted lookup.

for example to lookup value of setting BLAH you would do

from askbot.conf import settings as askbot_settings

askbot_settings.BLAH

NOTE that at the moment there is distinction between settings
(django settings) and askbot_settings (forum.deps.livesettings)

the value will be taken from askbot.deps.livesettings database or cache
note that during compilation phase database is not accessible
for the most part, so actual values are reliably available only 
at run time

askbot.deps.livesettings is a module developed for satchmo project
"""
from django.conf import settings as django_settings
from django.core.cache import cache
from django.contrib.sites.models import Site
from django.utils.translation import get_language
from django.utils.translation import activate as activate_language
import askbot
from askbot.deps.livesettings import SortedDotDict, config_register
from askbot.deps.livesettings.functions import config_get
from askbot.deps.livesettings import signals

class ConfigSettings(object):
    """A very simple Singleton wrapper for settings
    a limitation is that all settings names using this class
    must be distinct, even though they might belong
    to different settings groups
    """
    __instance = None
    __group_map = {}

    def __init__(self):
        """assigns SortedDotDict to self.__instance if not set"""
        if ConfigSettings.__instance == None:
            ConfigSettings.__instance = SortedDotDict()
        self.__dict__['_ConfigSettings__instance'] = ConfigSettings.__instance
        self.__ordering_index = {}

    def __getattr__(self, key):
        """value lookup returns the actual value of setting
        not the object - this way only very minimal modifications
        will be required in code to convert an app
        depending on django.conf.settings to askbot.deps.livesettings
        """
        hardcoded_setting = getattr(django_settings, 'ASKBOT_' + key, None)
        if hardcoded_setting is None:
            return getattr(self.__instance, key).value
        else:
            return hardcoded_setting

    def get_default(self, key):
        """return the defalut value for the setting"""
        return getattr(self.__instance, key).default

    def get_description(self, key):
        """returns descriptive title of the setting"""
        return unicode(getattr(self.__instance, key).description)

    def reset(self, key):
        """returns setting to the default value"""
        self.update(key, self.get_default(key))

    def get_value_for_site(self, site, key):
        """returns string value for the setting for a given site"""
        from askbot.deps.livesettings.models import Setting, LongSetting
        try:
            #note that we use custom manager "all_objects" to query by site
            setting = LongSetting.all_objects.get(site=site, key=key)
        except LongSetting.DoesNotExist:
            try:
                #note that we use custom manager "all_objects" to query by site
                setting = Setting.all_objects.get(site=site, key=key)
            except Setting.DoesNotExist:
                return None
        return setting.value

    def update(self, key, value, lang=None):
        try:
            setting = config_get(self.__group_map[key], key)
            if setting.localized:
                lang = lang or get_language()
            else:
                lang = None
            setting.update(value, lang)

        except:
            from askbot.deps.livesettings.models import Setting
            lang = lang or get_language()
            lang_postfix = '_' + lang.upper()
            #first try localized setting
            try:
                setting = Setting.objects.get(key=key + lang_postfix)
            except Setting.DoesNotExist:
                setting = Setting.objects.get(key=key)

            setting.value = value
            setting.group = self.__group_map[key]
            setting.site = Site.objects.get_current()
            setting.save()
        #self.prime_cache()

    def register(self, value):
        """registers the setting
        value must be a subclass of askbot.deps.livesettings.Value
        """
        key = value.key
        group_key = value.group.key

        ordering = self.__ordering_index.get(group_key, None)
        if ordering:
            ordering += 1
            value.ordering = ordering
        else:
            ordering = 1
            value.ordering = ordering
        self.__ordering_index[group_key] = ordering

        if key not in self.__instance:
            self.__instance[key] = config_register(value)
            self.__group_map[key] = group_key

    def as_dict(self):
        cache_key = get_bulk_cache_key()
        settings = cache.get(cache_key)
        if settings:
            return settings
        else:
            self.prime_cache(cache_key)
            return cache.get(cache_key)

    @classmethod
    def prime_cache(cls, cache_key, language_code=None, **kwargs):
        """reload all settings into cache as dictionary
        """
        from askbot.utils.translation import get_language
        language_code = language_code or get_language()
        activate_language(language_code)

        out = dict()
        for key in cls.__instance.keys():
            #todo: this is odd that I could not use self.__instance.items() mapping here
            hardcoded_setting = getattr(django_settings, 'ASKBOT_' + key, None)
            if hardcoded_setting is None:
                out[key] = cls.__instance[key].value
            else:
                out[key] = hardcoded_setting
        cache.set(cache_key, out)


def get_bulk_cache_key(language_code=None):
    from askbot.utils.translation import get_language
    language_code = language_code or get_language()
    return 'askbot-settings-%d-%s' % (django_settings.SITE_ID, language_code)


def prime_cache_handler(*args, **kwargs):
    from askbot.utils.translation import get_language
    current_language_code = get_language()

    if askbot.is_multilingual():
        language_codes = dict(django_settings.LANGUAGES).keys()
    else:
        language_codes = (django_settings.LANGUAGE_CODE,)
    
    for language_code in language_codes:
        cache_key = get_bulk_cache_key(language_code)
        ConfigSettings.prime_cache(cache_key, language_code)

    activate_language(current_language_code)

signals.configuration_value_changed.connect(prime_cache_handler)
#settings instance to be used elsewhere in the project
settings = ConfigSettings()
