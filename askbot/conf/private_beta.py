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

settings.register(
    livesettings.BooleanValue(
        PRIVATE_BETA,
        'PRIVATEBETA_ENABLE_CUSTOM_MESSAGE',
        description=_('Enable Custom invite email message.'),
        default=False,
        help_text = _("Please fill out the <b>Private beta custom message</b> setting")
        )
    )

settings.register(
    livesettings.StringValue(
        PRIVATE_BETA,
        'PRIVATEBETA_CUSTOM_SUBJECT',
        description=_('Custom invite email message subject.'),
        default= _('Your invitation for Q&A site')
    )
)

settings.register(
    livesettings.LongStringValue(
        PRIVATE_BETA,
        'PRIVATEBETA_CUSTOM_MESSAGE',
        description=_('Custom invite email message.'),
        default= _('Howdy!!!'
                   'You are invited to start your Q&A community at Askbot.'
                   'This link will get you started:  http://{{ domain_name }}/{{code}}'),
        help_text = _('You can add your text here do not forget to include'
                      'the variables http://{{domain_name}}/{{code}}'
                      )
    )
)
