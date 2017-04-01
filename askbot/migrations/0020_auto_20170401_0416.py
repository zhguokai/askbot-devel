# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0019_auto_20170226_1713'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='space',
            options={'ordering': ['order_number']},
        ),
        migrations.AddField(
            model_name='askwidget',
            name='space',
            field=models.ForeignKey(blank=True, to='askbot.Space', null=True),
        ),
        migrations.AddField(
            model_name='questionwidget',
            name='space',
            field=models.ForeignKey(blank=True, to='askbot.Space', null=True),
        ),
    ]
