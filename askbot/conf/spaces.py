"""
Settings responsible for display of questions lists
"""
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat
from askbot.conf.settings_wrapper import settings
from askbot.conf.super_groups import DATA_AND_FORMATTING
from askbot.deps import livesettings

SPACES = livesettings.ConfigurationGroup(
    'SPACES',
    _('Spaces'),
    super_group=DATA_AND_FORMATTING,
    #description=_('Spaces are sub-forums or sections of questions')
)

settings.register(
    livesettings.BooleanValue(
        SPACES,
        'SPACES_ENABLED',
        default=True,
        description=_('Enable Spaces'),
        help_text=_('Spaces are sub-forums or sections of questions')
    )
)

MAIN_PAGE_MODE_CHOICES = (
    ('redirect', _('Redirect to primary space')),
    ('list-spaces', _('List available spaces'))
)

settings.register(
    livesettings.StringValue(
        SPACES,
        'MAIN_PAGE_MODE',
        description=_('Main page functionality'),
        help_text=_('Used only when spaces are enabled'),
        default='redirect',
        choices=MAIN_PAGE_MODE_CHOICES
    )
)

settings.register(
    livesettings.LongStringValue(
        SPACES,
        'SPACES_PAGE_DESCRIPTION',
        description=_('Main page introduction text'),
        help_text=_('Used only when main page shows list of spaces'),
        default=string_concat(
            _('Welcome to our community!'),
            ' ',
            _('Please navigate to one of the sections shown on this page.')
        )
    )
)
