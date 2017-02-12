# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0016_set_space_to_threads'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thread',
            name='space',
            field=models.ForeignKey(related_name='threads', to='askbot.Space'),
        ),
    ]
