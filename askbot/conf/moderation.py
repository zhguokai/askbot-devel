"""Settings to control content moderation"""

from askbot.conf.settings_wrapper import settings
from askbot.conf.super_groups import DATA_AND_FORMATTING
from askbot.deps.livesettings import ConfigurationGroup
from askbot.deps.livesettings import BooleanValue
from askbot.deps.livesettings import StringValue
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

def empty_cache_callback(old_value, new_value):
    """used to clear cache on change of certain values"""
    if old_value != new_value:
        #todo: change this to warmup cache
        cache.clear()
    return new_value

MODERATION = ConfigurationGroup(
                    'MODERATION',
                    _('Content moderation'),
                    super_group=DATA_AND_FORMATTING
                )

CONTENT_MODERATION_MODE_CHOICES = (
    ('flags', _('audit flagged posts')),
    ('audit', _('audit flagged posts and watched users')),
    ('premoderation', _('pre-moderate watched users and audit flagged posts')),
)

settings.register(
    StringValue(
        MODERATION,
        'CONTENT_MODERATION_MODE',
        choices=CONTENT_MODERATION_MODE_CHOICES,
        default='flags',
        description=_('Content moderation method'),
        update_callback=empty_cache_callback,
        help_text=_("Audit is made after the posts are published, pre-moderation prevents publishing before moderator's decision.")
    )
)

settings.register(
    BooleanValue(
        MODERATION,
        'ENABLE_TAG_MODERATION',
        default=False,
        description=_('Enable tag moderation'),
        help_text=_(
            'If enabled, any new tags will not be applied '
            'to the questions, but emailed to the moderators. '
            'To use this feature, tags must be optional.'
        )
    )
)
