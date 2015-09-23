from askbot import const
from django.conf import settings as django_settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from jsonfield import JSONField
from django_countries.fields import CountryField

class UserProfile(models.Model):
    #text_search_vector           | tsvector                 | 
    auth_user_ptr = models.OneToOneField(
                                User,
                                parent_link=True,
                                related_name='askbot_profile',
                                primary_key=True
                            )
    avatar_urls = JSONField(default={})
    status = models.CharField(
                            max_length=2,
                            default=const.DEFAULT_USER_STATUS,
                            choices=const.USER_STATUS_CHOICES
                        )
    is_fake = models.BooleanField(default=False)
    email_isvalid = models.BooleanField(default=False)
    email_key = models.CharField(max_length=32, null=True)
    #hardcoded initial reputaion of 1, no setting for this one
    reputation = models.PositiveIntegerField(default=const.MIN_REPUTATION)
    gravatar = models.CharField(max_length=32)
    #has_custom_avatar = models.BooleanField(default=False)
    avatar_type = models.CharField(
            max_length=1,
            choices=const.AVATAR_TYPE_CHOICES,
            default='n' #for real set by the init_avatar_type based
            #on the livesetting value
        )
    gold = models.SmallIntegerField(default=0)
    silver = models.SmallIntegerField(default=0)
    bronze = models.SmallIntegerField(default=0)
    #todo: remove const.QUESTIONS_PER_PAGE_USER_CHOICES, no longer used!
    last_seen = models.DateTimeField(default=timezone.now)
    #todo: maybe remove
    real_name = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=200, blank=True)
    #location field is actually city
    location = models.CharField(max_length=100, blank=True)
    country = CountryField(blank=True, null=True)
    show_country = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)
    about = models.TextField(blank=True)
    #interesting tags and ignored tags are to store wildcard tag selections only
    interesting_tags = models.TextField(blank=True)
    ignored_tags = models.TextField(blank=True)
    subscribed_tags = models.TextField(blank=True)
    email_signature = models.TextField(blank=True)
    show_marked_tags = models.BooleanField(default=True)
    email_tag_filter_strategy = models.SmallIntegerField(
            choices=const.TAG_EMAIL_FILTER_FULL_STRATEGY_CHOICES,
            default=const.EXCLUDE_IGNORED
        )
    display_tag_filter_strategy = models.SmallIntegerField(
            choices=const.TAG_DISPLAY_FILTER_STRATEGY_CHOICES,
            default=const.INCLUDE_ALL
        )
    new_response_count = models.IntegerField(default=0)
    seen_response_count = models.IntegerField(default=0)
    consecutive_days_visit_count = models.IntegerField(default=0)
    #list of languages for which user should receive email alerts
    languages = models.CharField(
                            max_length=128,
                            default=django_settings.LANGUAGE_CODE
                        )

    twitter_access_token = models.CharField(max_length=256, default='')
    twitter_handle = models.CharField(max_length=32, default='')
    social_sharing_mode = models.IntegerField(
                                default=const.SHARE_NOTHING,
                                choices=const.SOCIAL_SHARING_MODE_CHOICES
                            )

    class Meta:
        app_label = 'askbot'
