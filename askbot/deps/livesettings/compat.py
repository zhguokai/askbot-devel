"""django version compatibility functions"""
from django.conf import settings

def get_cache_timeout():
    if hasattr(settings, 'CACHES'):
        return getattr(settings, 'LIVESETTINGS_CACHE_TIMEOUT', settings.CACHES['default']['TIMEOUT'])
    return getattr(settings, 'LIVESETTINGS_CACHE_TIMEOUT', settings.CACHE_TIMEOUT)


