# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from askbot import models as askbot_models

TRANS = {'good': 'S', 'bad': 'I'}

class Migration(DataMigration):
    
    def forwards(self, orm):
        """
        1. go through tag marks and translates 
           values of the ``reason`` field
           only use S - sub by email and I - ignore
        2. move User.interesting_tags to
           User.subscribed_tags
        """

        #existing tag marks
        for mark in askbot_models.MarkedTag.objects.all():
            mark.reason = TRANS[mark.reason]
            mark.save()

        #interesting_tags -> subscribed_tags
        for user in askbot_models.User.objects.all():
            user.subscribed_tags = user.interesting_tags
            user.interesting_tags =  ''
            user.save()
    
    def backwards(self, orm):
        "Write your backwards methods here."
        pass
    
    models = {
        
    }
    
    complete_apps = ['askbot_wrs_patch']
