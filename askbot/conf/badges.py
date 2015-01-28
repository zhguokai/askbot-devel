"""
Settings for reputation changes that apply to 
user in response to various actions by the same
users or others
"""
from askbot.conf.settings_wrapper import settings
from askbot.conf.super_groups import REP_AND_BADGES
from askbot.deps.livesettings import ConfigurationGroup
from askbot.deps.livesettings import IntegerValue
from askbot.deps.livesettings import BooleanValue
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat

BADGES = ConfigurationGroup(
                    'BADGES',
                    _('Badge settings'),
                    ordering=2,
                    super_group = REP_AND_BADGES
                )

def register_badge_settings(badge_slug=None, badge_name=None, params=None):
    settings.register(
        BooleanValue(
            BADGES,
            badge_slug + '_BADGE_ENABLED',
            default=True,
            description=_('Enable "%s" badge') % badge_name
        )
    )
    for param_slug, param_data in params.items():
        param_description = param_data[0]
        param_default = param_data[1]
        settings.register(
                IntegerValue(
                BADGES,
                badge_slug + '_BADGE_' + param_slug,
                description=string_concat(badge_name, ': ', param_description),
                default=param_default
            )
        )
        

register_badge_settings(
    'DISCIPLINED',
    _('Disciplined')),
    params={
        'MIN_UPVOTES': (_('minimum upvotes for deleted post'), 3)
    }
)

register_badge_settings(
    'PEER_PRESSURE',
    _('Peer pressure'),
    params={
        'MIN_DOWNVOTES': (_('minimum downvotes for deleted post'), 3)
    }
)

register_badge_settings(
    'TEACHER',
    _('Teacher'),
    params={
        'MIN_UPVOTES': (_('minimum upvotes for the answer'), 1)
    }
)

register_badge_settings(
    'NICE_ANSWER',
    _('Nice Answer'),
    params={
        'MIN_UPVOTES': (_('minimum upvotes for the answer'), 2)
    }
)

register_badge_settings(
    'GOOD_ANSWER',
    _('Good Answer'),
    params={
        'MIN_UPVOTES': (_('minimum upvotes for the answer'), 3)
    }
)

register_badge_settings(
    'GREAT_ANSWER',
    _('Great Answer'),
    params={
        'MIN_UPVOTES': (_('minimum upvotes for the answer'), 5)
    }
)

register_badge_settings(
    'NICE_QUESTION',
    _('Nice Question'),
    params={
        'MIN_UPVOTES': (_('minimum upvotes for the question'), 2)
    }
)

register_badge_settings(
    'GOOD_QUESTION',
    _('Good Question'),
    params={
        'MIN_UPVOTES': (_('minimum upvotes for the question'), 3)
    }
)

register_badge_settings(
    'GREAT_QUESTION',
    _('Great Question'),
    params={
        'MIN_UPVOTES': (_('minimum upvotes for the question'), 5)
    }
)

register_badge_settings(
    'POPULAR_QUESTION',
    _('Popular Question'),
    params={
        'MIN_VIEWS': (_('minimum views'), 15)
    }
)

register_badge_settings(
    'NOTABLE_QUESTION',
    _('Notable Question'),
    params={
        'MIN_VIEWS': (_('minimum views'), 25)
    }
)

register_badge_settings(
    'FAMOUS_QUESTION',
    _('Famous Question') 
    params={
        'MIN_VIEWS': (_('minimum views'), 50)
    }
)

register_badge_settings(
    'SELF_LEARNER',
    _('Self-Learner'),
    params={
        'MIN_UPVOTES': (_('minimum answer upvotes'), 1)
    }
)

register_badge_settings(
    'CIVIC_DUTY',
    _('Civic Duty'),
    params={
        'MIN_VOTES': (_('minimum votes'), 100)
    }
)

register_badge_settings(
)
    'ENLIGHTENED',
    'MIN_UPVOTES',
    3,
    _('Enlightened Duty'),
    _('minimum upvotes')

settings.register(
    IntegerValue(
        BADGES,
        'GURU_BADGE_MIN_UPVOTES',
        default=5,
        description=_('Guru: minimum upvotes')
    )
)

settings.register(
    IntegerValue(
        BADGES,
        'NECROMANCER_BADGE_MIN_UPVOTES',
        default=1,
        description=_('Necromancer: minimum upvotes')
    )
)

settings.register(
    IntegerValue(
        BADGES,
        'NECROMANCER_BADGE_MIN_DELAY',
        default=30,
        description=_('Necromancer: minimum delay in days')
    )
)

settings.register(
    IntegerValue(
        BADGES,
        'ASSOCIATE_EDITOR_BADGE_MIN_EDITS',
        default=20,
        description=_('Associate Editor: minimum number of edits')
    )
)

settings.register(
    IntegerValue(
        BADGES,
        'FAVORITE_QUESTION_BADGE_MIN_STARS',
        default=3,
        description=_('Favorite Question: minimum stars')
    )
)

settings.register(
    IntegerValue(
        BADGES,
        'STELLAR_QUESTION_BADGE_MIN_STARS',
        default=5,
        description=_('Stellar Question: minimum stars')
    )
)

settings.register(
    IntegerValue(
        BADGES,
        'COMMENTATOR_BADGE_MIN_COMMENTS',
        default=10,
        description=_('Commentator: minimum comments')
    )
)

settings.register(
    IntegerValue(
        BADGES,
        'TAXONOMIST_BADGE_MIN_USE_COUNT',
        default = 5,
        description = _('Taxonomist: minimum tag use count')
    )
)

settings.register(
    IntegerValue(
        BADGES,
        'ENTHUSIAST_BADGE_MIN_DAYS',
        default = 5,
        description = _('Enthusiast: minimum days')
    )
)
