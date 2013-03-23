"""
Settings responsible for display of questions lists
"""
from askbot.conf.settings_wrapper import settings
from askbot.conf.super_groups import DATA_AND_FORMATTING
from askbot.deps import livesettings
from django.utils.translation import ugettext_lazy as _

MAIN_PAGES = livesettings.ConfigurationGroup(
            'MAIN_PAGES',
            _('Questions page'), 
            super_group=DATA_AND_FORMATTING
        )

settings.register(
    livesettings.StringValue(
        MAIN_PAGES,
        'ALL_SCOPE_ENABLED',
        default=True,
        description=_('Enable "All Questions" selector'),
    )
)

settings.register(
    livesettings.BooleanValue(
        MAIN_PAGES,
        'UNANSWERED_SCOPE_ENABLED',
        default=True,
        description=_('Enable "Unanswered Questions" selector'),
    )
)

settings.register(
    livesettings.BooleanValue(
        MAIN_PAGES,
        'FOLLOWED_SCOPE_ENABLED',
        default=True,
        description=_('Enable "Followed Questions" selector'),
    )
)

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
        description=_('Default questions selector for the authenticated users')
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
        description=_('Default questions selector for the anonymous users')
    )
)
