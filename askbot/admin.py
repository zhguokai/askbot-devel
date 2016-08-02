# -*- coding: utf-8 -*-
"""
:synopsis: connector to standard Django admin interface

To make more models accessible in the Django admin interface, add more classes subclassing ``django.contrib.admin.Model``

Names of the classes must be like `SomeModelAdmin`, where `SomeModel` must
exactly match name of the model used in the project
"""
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext as _
from askbot import models


class PostAdmin(admin.ModelAdmin):
    date_hierarchy = 'added_at'
    list_display = ('author', 'post_type', 'added_at')
    list_filter = ('added_at', 'post_type')
    ordering = ('-added_at',)
    fieldsets = (
        (None, {
            'fields': (
                ('author', 'post_type', 'added_at'),
                ('old_question_id', 'old_answer_id', 'old_comment_id'),
                ('parent', 'thread', 'current_revision'),
                ('endorsed', 'endorsed_by', 'endorsed_at'),
                'approved',
                ('deleted', 'deleted_at', 'deleted_by'),
                ('wiki', 'wikified_at'),
                ('locked', 'locked_by', 'locked_at'),
                ('points', 'vote_up_count', 'vote_down_count'),
                'comment_count',
                'offensive_flag_count',
                ('last_edited_at', 'last_edited_by'),
                'language_code',
                ('html', 'text'),
                'summary',
                'is_anonymous',
            )
        }),
    )


class AnonymousQuestionAdmin(admin.ModelAdmin):
    """AnonymousQuestion admin class"""


class TagAdmin(admin.ModelAdmin):
    """Tag admin class"""


class VoteAdmin(admin.ModelAdmin):
    """  admin class"""


class FavoriteQuestionAdmin(admin.ModelAdmin):
    """  admin class"""


class PostRevisionAdmin(admin.ModelAdmin):
    date_hierarchy = 'revised_at'
    list_display = ('post', 'author', 'revised_at')
    list_filter = ('revised_at', 'approved', 'is_anonymous')
    ordering = ('-revised_at',)
    fieldsets = (
        (None, {
            'fields': (
                ('post', 'revision', 'author', 'revised_at'),
                ('summary', 'text'),
                ('approved', 'approved_by', 'approved_at'),
                ('by_email', 'email_address'),
            )
        }),
        (_("Specific to question"), {
            'fields': (
                'title',
                'tagnames',
                'is_anonymous',
                'ip_addr',
            )
        }),
    )


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
admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Vote, VoteAdmin)
admin.site.register(models.FavoriteQuestion, FavoriteQuestionAdmin)
admin.site.register(models.PostRevision, PostRevisionAdmin)
admin.site.register(models.Award, AwardAdmin)
admin.site.register(models.Repute, ReputeAdmin)
admin.site.register(models.Activity, ActivityAdmin)
admin.site.register(models.BulkTagSubscription)
