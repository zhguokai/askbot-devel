# -*- coding: utf-8 -*-
"""
:synopsis: connector to standard Django admin interface

To make more models accessible in the Django admin interface, add more classes subclassing ``django.contrib.admin.Model``

Names of the classes must be like `SomeModelAdmin`, where `SomeModel` must
exactly match name of the model used in the project
"""
from django.contrib import admin
from askbot import models
from askbot import const

admin.site.register(models.Tag)
admin.site.register(models.Vote)
admin.site.register(models.FavoriteQuestion)
admin.site.register(models.PostRevision)
admin.site.register(models.Award)
admin.site.register(models.Repute)
admin.site.register(models.BulkTagSubscription)
admin.site.register(models.Space)
admin.site.register(models.Feed)

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'active_at', 'activity_type', 'content_type', 'object_id', 'content_object')
    list_filter = ('activity_type', 'content_type', 'user')
admin.site.register(models.Activity, ActivityAdmin)

class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'level')
    list_filter = ('level', 'user')
admin.site.register(models.GroupMembership, GroupMembershipAdmin)

class EmailFeedSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscriber', 'email_tag_filter_strategy', 'feed_type', 'frequency', 'added_at', 'reported_at' )
    list_filter = ('frequency', 'feed_type', 'subscriber')
    
    def email_tag_filter_strategy(self, obj):
        if obj.feed_type == 'q_all':
            strategy = obj.subscriber.email_tag_filter_strategy
            if strategy == const.INCLUDE_ALL:
                return 'all tags'
            elif strategy == const.EXCLUDE_IGNORED:
                return 'exclude ignored tags'
            elif strategy == const.INCLUDE_INTERESTING:
                return 'only interesting tags'
            elif strategy == const.INCLUDE_SUBSCRIBED:
                return 'include subscribed'
            else:
                return 'invalid'
        else:
            return 'n/a'
admin.site.register(models.EmailFeedSetting, EmailFeedSettingAdmin)

class QuestionViewAdmin(admin.ModelAdmin):
    list_display = ('who', 'question', 'when')
    list_filter = ('who',)
admin.site.register(models.QuestionView, QuestionViewAdmin)

class PostAdmin(admin.ModelAdmin):
    # TODO: show groups
    list_display = ('post_type', 'thread', 'author', 'added_at', 'deleted')
    list_filter = ('deleted', 'post_type', 'author')
admin.site.register(models.Post, PostAdmin)

class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'added_at', 'last_activity_at', 'last_activity_by', 'deleted', 'closed')
    list_filter = ('deleted', 'closed', 'last_activity_by')
admin.site.register(models.Thread, ThreadAdmin)

