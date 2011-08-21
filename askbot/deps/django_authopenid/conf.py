from django.conf import settings as django_settings
from askbot.deps.django_authopenid import default_settings
from import_utils import import_module_from

class MultiRegistry(object):
    """allows access to attributes via dotted python notation.
    Attributes may be stored in multiple objects.

    Upon access, objects will be tried in the order they were
    inserted into the registry.

    For example, if we have two settings like objects:
    A with attribute 'a'
    and B with attribute 'b'
    and we construct registry as:

    >>>r = MultiRegistry()
    >>>r.append(A)
    >>>r.append(B)

    then access the registry as:

    r.b - attrubute b will be first looked
    up in the object A, then in the object B, where
    it will be found.

    If the attribute is not found, attribute error will be 
    raised.
    """
    def __init__(self):
        self.registry_stores = list()

    def append(self, registry_store):
        """adds a registry object to the list of
        """
        self.registry_stores.append(registry_store)

    def __getattr__(self, attr_name):
        for store in self.registry_stores:
            if hasattr(store, attr_name):
                return getattr(store, attr_name)
        raise AttributeError('setting %s not found' % attr_name)

settings = MultiRegistry()
settings.append(django_settings)

extra_settings_path = getattr(django_settings, 'EXTRA_SETTINGS_MODULE', None)
if extra_settings_path:
    module = import_module_from(extra_settings_path)
    settings.append(module)

settings.append(default_settings)
