# -*- coding: utf-8 -*-
"""
:synopsis: connector to standard Django admin interface

To make more models accessible in the Django admin interface, add more classes subclassing ``django.contrib.admin.Model``

Names of the classes must be like `SomeModelAdmin`, where `SomeModel` must
exactly match name of the model used in the project
"""
from django.conf import settings as django_settings
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from askbot import models
from askbot import const
from askbot.deps.django_authopenid.models import UserEmailVerifier


TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


admin.site.register(models.Vote)
admin.site.register(models.FavoriteQuestion)
admin.site.register(models.Award)
admin.site.register(models.Repute)
admin.site.register(models.BulkTagSubscription)

class UserEmailVerifierAdmin(admin.ModelAdmin):
    list_display = ('key', 'verified', 'expires_on')
admin.site.register(UserEmailVerifier, UserEmailVerifierAdmin)

class InSite(SimpleListFilter):
    title = 'site membership'
    parameter_name = 'name'

    def lookups(self, request, model_admin):
        return tuple([(s.id, 'in site \'%s\''%s.name) for s in Site.objects.all()])
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sites__id=self.value())
        else: 
            return queryset

class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'language_code', 'created_by', 'deleted', 'status', 'in_sites', 'used_count') 
    list_filter = ('deleted', 'status', 'language_code', InSite)
    search_fields = ('name',)

    def in_sites(self, obj):
        return ', '.join(obj.sites.all().values_list('name', flat=True))
admin.site.register(models.Tag, TagAdmin)

class SpaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
admin.site.register(models.Space, SpaceAdmin)

class FeedAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'default_space', 'redirect', 'site')
admin.site.register(models.Feed, FeedAdmin)

class FeedToSpaceAdmin(admin.ModelAdmin):
    list_display = ('feed', 'space')
    list_filter = ('feed', 'space')
    search_fields = ('feed__name', 'space__name')
admin.site.register(models.FeedToSpace, FeedToSpaceAdmin)

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'active_at', 'activity_type', 'question', 'content_type', 'object_id', 'content_object', 'recipients_list', 'receiving_users_list')
    list_filter = ('activity_type', 'content_type')
    search_fields = ('user__username', 'object_id', 'question__id', 'question__thread__id', 'question__thread__title')

    def recipients_list(self, obj):
        return ', '.join(obj.recipients.all().values_list('username', flat=True))

    def receiving_users_list(self, obj):
        return ', '.join(obj.receiving_users.all().values_list('username', flat=True))
admin.site.register(models.Activity, ActivityAdmin)

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

class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'level')
    list_filter = ('level',)
    search_fields = ('user__username',)
admin.site.register(models.GroupMembership, GroupMembershipAdmin)

class EmailFeedSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscriber', 'email_tag_filter_strategy', 'feed_type', 'frequency', 'added_at', 'reported_at' )
    list_filter = ('frequency', 'feed_type')
    search_fields = ('subscriber__username',)
    
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
    search_fields = ('who__username',)
admin.site.register(models.QuestionView, QuestionViewAdmin)

class PostToGroupInline(admin.TabularInline):
    model = models.PostToGroup
    extra = 1

class IsPrivate(SimpleListFilter):
    title = 'is private'
    parameter_name = 'is_private'

    def lookups(self, request, model_admin):
        return (('1', 'Yes'), ('0', 'No'))
    def queryset(self, request, queryset):
        global_group = models.Group.objects.get_global_group()
        if self.value() == '1':
            return queryset.exclude(groups__id=global_group.id)
        elif self.value() == '0':
            return queryset.filter(groups__id=global_group.id)
        else:
            return queryset

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_type', 'thread', 'author', 'text_30', 'added_at_with_seconds', 'deleted', 'in_groups', 'is_published', 'is_private', 'vote_up_count', 'language_code')
    list_filter = ('deleted', IsPrivate, 'post_type', 'language_code', 'vote_up_count')
    search_fields = ('id', 'thread__title', 'text', 'author__username')
    inlines = (PostToGroupInline,)

    def text_30(self, obj):
        return obj.text[:30]

    def added_at_with_seconds(self, obj):
        return obj.added_at.strftime(TIME_FORMAT)
    added_at_with_seconds.admin_order_field = 'added_at'

    def in_groups(self, obj):
        return ', '.join(obj.groups.exclude(name__startswith=models.user.PERSONAL_GROUP_NAME_PREFIX).values_list('name', flat=True))

    def is_published(self, obj):
        return obj.thread._question_post().author.get_personal_group() in obj.groups.all()
admin.site.register(models.Post, PostAdmin)

class PostRevisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_id', 'post_type', 'thread_name', 'revision', 'revised_at_with_seconds', 'author', 'approved', 'is_minor', 'text_start')
    list_filter = ('approved', 'is_minor', 'revision')
    search_fields = ('text', 'author__username', 'post__id', 'post__thread__title')
    ordering = ('-id',)

    def post_id(self, obj):
        return obj.post.id

    def post_type(self, obj):
        return obj.post.post_type

    def thread_name(self, obj):
        return obj.post.thread.title

    def revised_at_with_seconds(self, obj):
        return obj.revised_at.strftime(TIME_FORMAT)
    revised_at_with_seconds.admin_order_field = 'revised_at'

    def text_start(self, obj):
        return obj.text[:30]
admin.site.register(models.PostRevision, PostRevisionAdmin)

class ThreadToGroupInline(admin.TabularInline):
    model = models.ThreadToGroup
    extra = 1

class SpacesInline(admin.TabularInline):
    model = models.Space.questions.through
    extra = 1

class TagsInline(admin.TabularInline):
    model = models.Thread.tags.through
    extra = 1

class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'added_at_with_seconds', 'last_activity_at_with_seconds', 'last_activity_by', 'answer_count', 'deleted', 'closed', 'site', 'in_spaces', 'in_groups', 'has_tags', 'is_private', 'language_code')
    list_filter = ('deleted', 'closed', 'language_code', 'site')
    search_fields = ('last_activity_by__username', 'title', 'tags__name')
    inlines = (ThreadToGroupInline, SpacesInline, TagsInline)

    def added_at_with_seconds(self, obj):
        return obj.added_at.strftime(TIME_FORMAT)
    added_at_with_seconds.admin_order_field = 'added_at'

    def last_activity_at_with_seconds(self, obj):
        return obj.last_activity_at.strftime(TIME_FORMAT)
    last_activity_at_with_seconds.admin_order_field = 'last_activity_at'

    def in_groups(self, obj):
        return ', '.join(obj.groups.exclude(name__startswith=models.user.PERSONAL_GROUP_NAME_PREFIX).values_list('name', flat=True))

    def in_spaces(self, obj):
        return ', '.join(obj.spaces.all().values_list('name', flat=True))

    def has_tags(self, obj):
        return ', '.join(obj.tags.all().values_list('name', flat=True))
admin.site.register(models.Thread, ThreadAdmin)

class NonPersonalGroupFilter(SimpleListFilter):
    title = 'non-personal group'
    parameter_name = 'non_personal_group'

    def lookups(self, request, model_admin):
        return tuple([(group.id, "%s group"%group.name) for group in models.Group.objects.exclude(name__contains=models.user.PERSONAL_GROUP_NAME_PREFIX)])
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(group__id=self.value())
        else:
            return queryset

class AskWidgetAdmin(admin.ModelAdmin):
    list_display = ('id', 'site', 'title', 'group', 'tag', 'include_text_field', 'has_inner_style', 'has_outer_style')
    list_filter = ('include_text_field', NonPersonalGroupFilter)
    search_fields = ('title', 'tag')

    def has_inner_style(self, obj):
        return obj.inner_style.strip() != u''

    def has_outer_style(self, obj):
        return obj.outer_style.strip() != u''
admin.site.register(models.AskWidget, AskWidgetAdmin)

class QuestionWidgetAdmin(admin.ModelAdmin):
    list_display = ('id', 'site', 'title', 'question_number', 'tagnames', 'group', 'has_search_query', 'order_by', 'has_style')
    list_filter = (NonPersonalGroupFilter,)
    search_fields = ('title', 'tagnames')

    def has_style(self, obj):
        return obj.style.strip() != u''

    def has_search_query(self, obj):
        return obj.search_query.strip() != u''
admin.site.register(models.QuestionWidget, QuestionWidgetAdmin)

class DraftQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'title', 'tagnames')
    search_fields = ('author__username', 'title', 'tagnames')
admin.site.register(models.DraftQuestion, DraftQuestionAdmin)

class ReplyAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'user', 'reply_action')
    list_display_links = ('id', 'address')
    search_fields = ('address', 'user__username')
    list_filter = ('reply_action',)
admin.site.register(models.ReplyAddress, ReplyAddressAdmin)


from django.contrib.sites.models import Site
try:
    admin.site.unregister(Site)
finally:
    from django.contrib.sites.admin import SiteAdmin as OrigSiteAdmin
    class SiteAdmin(OrigSiteAdmin):
        list_display = ('id',) + OrigSiteAdmin.list_display
    admin.site.register(Site, SiteAdmin)

class SubscribedToSite(InSite):
    title = 'subscribed to site'

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(subscribed_sites__id=self.value())
        else: 
            return queryset

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('auth_user', 'default_site', 'subs_sites', 'primary_group')
    list_filter = ('default_site', SubscribedToSite)
    search_fields = ('auth_user__username',)
    filter_horizontal = ('subscribed_sites',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'primary_group':
            global_group = models.Group.objects.get_global_group()
            groups = models.Group.objects.exclude(pk=global_group.id)
            groups = groups.exclude_personal()

            kwargs['queryset'] = groups

        return super(UserProfileAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def subs_sites(self, obj):
        return ', '.join(obj.subscribed_sites.all().values_list('name', flat=True))
admin.site.register(models.UserProfile, UserProfileAdmin)

from django.contrib.auth.models import User
try:
    admin.site.unregister(User)
finally:
    class InGroup(SimpleListFilter):
        title = 'group membership'
        parameter_name = 'in_group'

        def lookups(self, request, model_admin):
            return tuple([(g.id, 'in group \'%s\''%g.name) for g in models.Group.objects.exclude(name__startswith=models.user.PERSONAL_GROUP_NAME_PREFIX)])
        def queryset(self, request, queryset):
            if self.value():
                return queryset.filter(groups__id=self.value())
            else: 
                return queryset

    class _UserBooleanMethodListFilter(SimpleListFilter):
        def lookups(self, request, model_admin):
            return (('true', 'yes'), ('false', 'no'))

        def queryset(self, request, queryset):
            if self.value():
                target_boolean = self.value() == 'true'
                admin_ids = []
                for user in User.objects.all():
                    if bool(getattr(user, self.method)()) == target_boolean:
                        admin_ids.append(user.id)
                return queryset.filter(id__in=admin_ids)
            else:
                return queryset

    class IsAdministrator(_UserBooleanMethodListFilter):
        method = 'is_administrator'
        title = 'is administrator'
        parameter_name = 'is_administrator'

    class IsModerator(_UserBooleanMethodListFilter):
        method = 'is_moderator'
        title = 'is moderator'
        parameter_name = 'is_moderator'

    class SeesThreadsInLanguage(SimpleListFilter):
        title = "sees Threads in language"
        parameter_name = "sees_threads_in_lang"
        
        def lookups(self, request, model_admin):
            return django_settings.LANGUAGES

        def queryset(self, request, queryset):
            if self.value():
                return queryset.filter(languages__icontains=self.value())
            return queryset

    from django.contrib.auth.admin import UserAdmin as OrigUserAdmin
    class UserAdmin(OrigUserAdmin):
        list_display = OrigUserAdmin.list_display + ('languages', 
            'date_joined', 'reputation', 
            'is_administrator', 'status', 'is_moderator', 'is_fake', 'email_isvalid',
            'my_interesting_tags', 'interesting_tag_wildcards',
            'my_ignored_tags', 'ignored_tag_wildcards', 
            'my_subscribed_tags', 'subscribed_tag_wildcards',
            'email_tag_filter_strategy', 'display_tag_filter_strategy', 
            'get_groups', 'get_primary_group', 'get_default_site')
        list_filter = OrigUserAdmin.list_filter + (IsAdministrator, 'status', IsModerator, 'is_fake', 'email_isvalid', 'email_tag_filter_strategy', 'display_tag_filter_strategy', SeesThreadsInLanguage, InGroup)

        def interesting_tag_wildcards(self, obj):
            return ', '.join(obj.interesting_tags.strip().split())
        def my_interesting_tags(self, obj):
            return ', '.join(obj.get_marked_tags('good').values_list('name', flat=True))

        def ignored_tag_wildcards(self, obj):
            return ', '.join(obj.ignored_tags.strip().split())
        def my_ignored_tags(self, obj):
            return ', '.join(obj.get_marked_tags('bad').values_list('name', flat=True))

        def subscribed_tag_wildcards(self, obj):
            return ', '.join(obj.subscribed_tags.strip().split())
        def my_subscribed_tags(self, obj):
            return ', '.join(obj.get_marked_tags('subscribed').values_list('name', flat=True))
    admin.site.register(User, UserAdmin)

try:
    from avatar.models import Avatar
except ImportError:
    pass # avatar not installed, so no matter
else:
    from django.contrib.admin.sites import NotRegistered
    try:
        admin.site.unregister(Avatar)
    except NotRegistered:
        print u"Move 'avatar' above 'askbot' in INSTALLED_APPS to get a more useful admin view for Avatar model" 
    else:
        class AvatarAdmin(admin.ModelAdmin):
            list_display = ('id', 'user', 'avatar', 'primary', 'date_uploaded')
            list_filter = ('primary', 'date_uploaded')
            search_fields = ('user__username', 'user__email', 'avatar')
        admin.site.register(Avatar, AvatarAdmin)

