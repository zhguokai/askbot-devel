"""debugging utilities"""
import sys
from django.config import settings

def debug(message):
    """print debugging message to stderr"""
    site_id = django_settings.SITE_ID
    message = 'site_id=' + site_id + ' ' + message
    message = unicode(message).encode('utf-8')
    sys.stderr.write(message + '\n')
