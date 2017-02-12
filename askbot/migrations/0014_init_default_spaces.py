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

def init_primary_spaces(apps, schema_editor):
    Space = apps.get_model('askbot', 'Space')
    languages = get_languages()
    # TODO: validate list of languages - if it is default
    # then ask user to confirm operation, to avoid 
    # creating a space for every possible language that
    # django supports
    for lang in languages:
        space_name=get_default_space_name(lang)
        space = Space(
                    name=space_name,
                    slug=slugify(space_name),
                    language_code=lang,
                    order_number=0
                )
        space.save()


def delete_spaces(apps, schema_editor):
    Space = apps.get_model('askbot', 'Space')
    Space.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0013_auto_20170206_0344'),
    ]

    operations = [
        migrations.RunPython(init_primary_spaces, delete_spaces),
    ]
