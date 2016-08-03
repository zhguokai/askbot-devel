# -*- coding: utf-8 -*-
"""
:synopsis: connector to standard Django admin interface

To make more models accessible in the Django admin interface, add more classes subclassing ``django.contrib.admin.Model``

Names of the classes must be like `SomeModelAdmin`, where `SomeModel` must
exactly match name of the model used in the project
"""
from django.contrib import admin
from django.utils.translation import ugettext as _
from askbot import models
from django.contrib.admin import SimpleListFilter


class AnonymousQuestionAdmin(admin.ModelAdmin):
    """AnonymousQuestion admin class"""


class TagAdmin(admin.ModelAdmin):
    """Tag admin class"""


class VoteAdmin(admin.ModelAdmin):
    """  admin class"""


class FavoriteQuestionInline(admin.TabularInline):
    model = models.FavoriteQuestion


class ThreadAdmin(admin.ModelAdmin):
    date_hierarchy = 'added_at'
    list_display = ('title', 'added_at', 'last_activity_at', 'closed',
                    'deleted', 'approved')
    list_filter = ('added_at', 'last_activity_at', 'closed', 'deleted',
                   'approved')
    ordering = ('-added_at',)
    inlines = (FavoriteQuestionInline,)
    fieldsets = (
        (None, {
            'fields': (
                ('title', 'points'),
                'tags',
                ('followed_by'),
                ('closed', 'closed_by', 'closed_at', 'close_reason'),
                'deleted',
                ('approved', 'accepted_answer'),
            )
        }),
        (_("Question"), {
            'fields': (
                ('language_code', 'tagnames'),
                ('view_count', 'favourite_count', 'answer_count'),
                ('last_activity_by', 'last_activity_at'),
            )
        }),
    )


class ThreadToGroupAdmin(admin.ModelAdmin):
    list_display = ('thread', 'group', 'visibility')
    list_filter = ('visibility',)
    ordering = ('-thread',)
    fieldsets = (
        (None, {
            'fields': (
                ('thread', 'group', 'visibility'),
            )
        }),
    )


class QuestionViewAdmin(admin.ModelAdmin):
    date_hierarchy = 'when'
    list_display = ('who', 'question', 'when',)
    list_filter = ('when',)
    ordering = ('-when',)
    fieldsets = (
        (None, {
            'fields': (
                ('who', 'question', 'when'),
            )
        }),
    )


class FavoriteQuestionAdmin(admin.ModelAdmin):
    date_hierarchy = 'added_at'
    list_display = ('user', 'thread', 'added_at')
    list_filter = ('added_at',)
    ordering = ('-added_at',)
    fieldsets = (
        (None, {
            'fields': (
                ('user', 'thread', 'added_at'),
            )
        }),
    )


class PostRevisionAdmin(admin.ModelAdmin):
    """  admin class"""


class AwardAdmin(admin.ModelAdmin):
    """  admin class"""


class ReputeAdmin(admin.ModelAdmin):
    """  admin class"""


class ActivityAdmin(admin.ModelAdmin):
    date_hierarchy = 'active_at'
    list_display = ('user', 'activity_type', 'active_at')
    list_filter = ('active_at', 'activity_type')
    ordering = ('-active_at',)
    fieldsets = (
        (None, {
            'fields': (
                ('user', 'activity_type', 'active_at'),
                ('content_type', 'object_id'),
                ('question', 'is_auditted'),
                'summary',
            )
        }),
    )


class BadgeDataAdmin(admin.ModelAdmin):
    """admin class for BadgeData"""


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


admin.site.register(models.BadgeData)
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
admin.site.register(models.Thread, ThreadAdmin)
admin.site.register(models.question.ThreadToGroup, ThreadToGroupAdmin)
admin.site.register(models.QuestionView, QuestionViewAdmin)
