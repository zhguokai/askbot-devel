# -*- coding: utf-8 -*-
"""
:synopsis: connector to standard Django admin interface

To make more models accessible in the Django admin interface, add more classes subclassing ``django.contrib.admin.Model``

Names of the classes must be like `SomeModelAdmin`, where `SomeModel` must
exactly match name of the model used in the project
"""
from django.contrib import admin
from askbot import models
from django.contrib.admin import SimpleListFilter

class AnonymousQuestionAdmin(admin.ModelAdmin):
    """AnonymousQuestion admin class"""

class TagAdmin(admin.ModelAdmin):
    """Tag admin class"""

class VoteAdmin(admin.ModelAdmin):
    """  admin class"""

class FavoriteQuestionAdmin(admin.ModelAdmin):
    """  admin class"""

class PostRevisionAdmin(admin.ModelAdmin):
    """  admin class"""

class AwardAdmin(admin.ModelAdmin):
    """  admin class"""

class ReputeAdmin(admin.ModelAdmin):
    """  admin class"""

class ActivityAdmin(admin.ModelAdmin):
    """  admin class"""

class BadgeDataAdmin(admin.ModelAdmin):
    """admin class for BadgeData"""
admin.site.register(models.BadgeData)

class IsPersonal(SimpleListFilter):
    title = 'is personal group'
    parameter_name = 'is_personal'

    def lookups(self, request, model_admin):
        return (('1', 'Yes'), ('0', 'No'))
    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(name__contains=models.user.PERSONAL_GROUP_NAME_PREFIX)
        elif self.value() == '0':
            return queryset.exclude(name__contains=models.user.PERSONAL_GROUP_NAME_PREFIX)
        else: 
            return queryset

class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'logo_url', 'description', 'moderate_email', 'moderate_answers_to_enquirers', 'openness', 'is_vip', 'read_only')
    list_display_links = ('id', 'name')
    list_filter = (IsPersonal, 'moderate_email', 'moderate_answers_to_enquirers', 'openness', 'is_vip', 'read_only')
    search_fields = ('name', 'logo_url')
admin.site.register(models.Group, GroupAdmin)

admin.site.register(models.Post)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Vote, VoteAdmin)
admin.site.register(models.FavoriteQuestion, FavoriteQuestionAdmin)
admin.site.register(models.PostRevision, PostRevisionAdmin)
admin.site.register(models.Award, AwardAdmin)
admin.site.register(models.Repute, ReputeAdmin)
admin.site.register(models.Activity, ActivityAdmin)
admin.site.register(models.BulkTagSubscription)
