# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0014_init_default_spaces'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='space',
            field=models.ForeignKey(related_name='threads', to='askbot.Space', null=True),
        ),
    ]
