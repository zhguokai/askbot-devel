"""django version compatibility functions"""
from django.conf import settings

DEFAULT_CACHE_TIMEOUT = 6000

def get_cache_timeout():
    if hasattr(settings, 'CACHES'):
        return getattr(
                    settings,
                    'LIVESETTINGS_CACHE_TIMEOUT',
                    settings.CACHES['default'].get('TIMEOUT', DEFAULT_CACHE_TIMEOUT)
                )
    return getattr(
                settings,
                'LIVESETTINGS_CACHE_TIMEOUT',
                getattr(settings, 'CACHE_TIMEOUT', DEFAULT_CACHE_TIMEOUT)
            )


