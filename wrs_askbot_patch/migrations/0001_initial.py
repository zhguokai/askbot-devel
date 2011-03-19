# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        try:
            # Adding field 'User.subscibed_tags'
            db.add_column(u'auth_user', 'subscribed_tags', self.gf('django.db.models.fields.TextField')(blank=True, default = ''), keep_default=False)
        except:
            pass
    
    
    def backwards(self, orm):
        # Deleting field 'User.interesting_tags'
        db.delete_column('auth_user', 'subscribed_tags')
    
    
    models = {
        
    }
    
    complete_apps = ['askbot_wrs_patch']
