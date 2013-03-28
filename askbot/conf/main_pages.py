"""
Settings responsible for display of questions lists
"""
from askbot.conf.settings_wrapper import settings
from askbot.conf.super_groups import DATA_AND_FORMATTING
from askbot.deps import livesettings
from django.utils.translation import ugettext_lazy as _

MAIN_PAGES = livesettings.ConfigurationGroup(
            'MAIN_PAGES',
            _('Logic of the questions page'), 
            super_group=DATA_AND_FORMATTING
        )

settings.register(
    livesettings.BooleanValue(
        MAIN_PAGES,
        'ASK_BUTTON_ENABLED',
        default=True,
        description=_('Enable big Ask button'),
        help_text=_(
            'Disabling this button will reduce number of new questions. '
            'If this button is disabled, the ask button in the search menu '
            'will still be available.'
        )
    )
)

settings.register(
    livesettings.BooleanValue(
        MAIN_PAGES,
        'ALL_SCOPE_ENABLED',
        default=True,
        description=_('Enable "All Questions" selector'),
        help_text=_('At least one of these selectors must be enabled')
    )
)

settings.register(
    livesettings.BooleanValue(
        MAIN_PAGES,
        'UNANSWERED_SCOPE_ENABLED',
        default=True,
        description=_('Enable "Unanswered Questions" selector'),
        help_text=_('At least one of these selectors must be enabled')
    )
)

settings.register(
    livesettings.BooleanValue(
        MAIN_PAGES,
        'FOLLOWED_SCOPE_ENABLED',
        default=True,
        description=_('Enable "Followed Questions" selector'),
        help_text=_('At least one of these selectors must be enabled')
    )
)

def enable_default_selector_if_disabled(old_value, new_value):
    scope_switch_name = new_value.upper() + '_SCOPE_ENABLED'
    is_enabled = getattr(settings, scope_switch_name)
    if is_enabled is False:
        settings.update(scope_switch_name, True)
    return new_value

SCOPE_CHOICES_AUTHENTICATED = (
    ('all', _('All Questions')),
    ('unanswered', _('Unanswered Questions')),
    ('followed', _('Followed Questions'))
)

settings.register(
    livesettings.StringValue(
        MAIN_PAGES,
        'DEFAULT_SCOPE_AUTHENTICATED',
        choices=SCOPE_CHOICES_AUTHENTICATED,
        default='all',
        description=_('Default questions selector for the authenticated users'),
        update_callback=enable_default_selector_if_disabled
    )
)

SCOPE_CHOICES_ANONYMOUS = (#anonymous users can't see followed questions
    ('all', _('All Questions')),
    ('unanswered', _('Unanswered Questions')),
)

settings.register(
    livesettings.StringValue(
        MAIN_PAGES,
        'DEFAULT_SCOPE_ANONYMOUS',
        choices=SCOPE_CHOICES_ANONYMOUS,
        default='all',
        description=_('Default questions selector for the anonymous users'),
        update_callback=enable_default_selector_if_disabled
    )
)
