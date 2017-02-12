# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings as django_settings
from django.utils import translation
from django.db import models, migrations
import askbot
from askbot.utils.slug import slugify

def get_languages():
    if askbot.is_multilingual():
        return dict(django_settings.LANGUAGES).keys()
    else:
        return [django_settings.LANGUAGE_CODE]

def get_default_space_name(language_code):
    if django_settings.ASKBOT_TRANSLATE_URL:
        with translation.override(language_code):
            return translation.pgettext('url', 'questions')
    return 'questions'

def add_space_to_threads(apps, schema_editor):
    Space = apps.get_model('askbot', 'Space')
    Thread = apps.get_model('askbot', 'Thread')
    languages = get_languages()
    for lang in languages:
        space_name=get_default_space_name(lang)
        space = Space.objects.get(name=space_name)
        threads = Thread.objects.filter(language_code=lang)
        threads.update(space=space)


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0015_thread_space'),
    ]

    operations = [
        migrations.RunPython(add_space_to_threads)
    ]
