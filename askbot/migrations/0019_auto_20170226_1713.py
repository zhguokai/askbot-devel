# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import askbot.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0018_auto_20170213_1217'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpaceRedirect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.CharField(unique=True, max_length=128)),
                ('language_code', askbot.models.fields.LanguageCodeField(default=b'en', max_length=16, choices=[(b'en', b'English'), (b'fr', b'French')])),
                ('space', models.ForeignKey(related_name='redirects', to='askbot.Space')),
            ],
        ),
    ]
