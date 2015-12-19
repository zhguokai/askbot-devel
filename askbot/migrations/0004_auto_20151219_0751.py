# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core.management import call_command

def init_postgresql_fts(apps, schema_editor):
    conn = schema_editor.connection
    import pdb
    pdb.set_trace()
    if hasattr(conn, 'vendor') and conn.vendor == 'postgresql':
        call_command('init_postgresql_full_text_search')


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0003_auto_20151218_0909'),
    ]

    operations = [
        migrations.RunPython(init_postgresql_fts)
    ]
