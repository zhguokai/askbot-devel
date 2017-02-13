# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0017_auto_20170212_1112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='space',
            name='image',
            field=models.ImageField(null=True, upload_to=b'spaces', blank=True),
        ),
    ]
