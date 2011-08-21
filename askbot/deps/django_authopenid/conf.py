"""unifies django settings with an optional additional settings module
and default settings of this application"""
from django.conf import settings as django_settings
from askbot.deps.django_authopenid import default_settings
from import_utils import import_module_from
from multi_registry import MultiRegistry

settings = MultiRegistry()
settings.append(django_settings)

extra_settings_path = getattr(django_settings, 'EXTRA_SETTINGS_MODULE', None)
if extra_settings_path:
    module = import_module_from(extra_settings_path)
    settings.append(module)

settings.append(default_settings)
