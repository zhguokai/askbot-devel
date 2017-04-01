# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations

def add_space_to_widgets(apps, schema_editor):
    AskWidget = apps.get_model('askbot', 'AskWidget')
    QuestionWidget = apps.get_model('askbot', 'QuestionWidget')
    Space = apps.get_model('askbot', 'Space')
    spaces = Space.objects.all()

    widget_count = AskWidget.objects.count() + QuestionWidget.objects.count()
    if widget_count == 0:
        return 

    if spaces.count() == 0:
        raise Exception('Please create a space first. Cannot continue now')

    space = spaces[0]
    AskWidget.objects.update(space=space)
    QuestionWidget.objects.update(space=space)


def delete_space_from_widgets(apps, schema_editor):
    AskWidget = apps.get_model('askbot', 'AskWidget')
    AskWidget.objects.all().update(space=None)
    QuestionWidget = apps.get_model('askbot', 'QuestionWidget')
    QuestionWidget.objects.all().update(space=None)


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0020_auto_20170401_0416'),
    ]

    operations = [
        migrations.RunPython(add_space_to_widgets, delete_space_from_widgets),
    ]
