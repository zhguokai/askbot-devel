# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import get_language as _get_language

from haystack.constants import DEFAULT_ALIAS


def get_language():
    return _get_language()[:2]


def get_connection_prefix():
    return getattr(settings, 'ASKBOT_HAYSTACK_CONNECTION_PREFIX', 'default')


def alias_from_language(language):
    if language == settings.LANGUAGE_CODE:
        # if it's the default language, then we assume we're dealing with "default" connection.
        return DEFAULT_ALIAS

    connection_prefix = get_connection_prefix()

    if connection_prefix:
        connection = '{0}_{1}'.format(connection_prefix, language)
    else:
        connection = language
    return connection


def language_from_alias(alias):
    connection_prefix = get_connection_prefix()

    if alias == DEFAULT_ALIAS:
        language = settings.LANGUAGE_CODE
    else:
        language = alias.split('_')[-1]
    return language
