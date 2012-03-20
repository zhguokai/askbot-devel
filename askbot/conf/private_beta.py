"""Private Beta Mode settings"""
from askbot.deps import livesettings
from askbot.conf.settings_wrapper import settings
from askbot.conf.super_groups import REP_AND_BADGES

from django.utils.translation import ugettext as _
from django.conf import settings as django_settings

PRIVATE_BETA = livesettings.ConfigurationGroup(
                    'PRIVATEBETA_MODE',
                    _('Private beta settings'),
                    super_group = REP_AND_BADGES
                )

settings.register(
    livesettings.BooleanValue(
        PRIVATE_BETA,
        'ENABLE_PRIVATEBETA',
        description=_('Enable Private Beta mode.'),
        default=False
    )
)


settings.register(
    livesettings.IntegerValue(
        PRIVATE_BETA,
        'PRIVATEBETA_INVITE_DURATION',
        description=_('Invite duration (days)'),
        default=15
    )
)

