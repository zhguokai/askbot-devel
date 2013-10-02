"""
General skin settings
"""
from askbot.conf.settings_wrapper import settings
from askbot.deps.livesettings import ConfigurationGroup
from askbot.deps.livesettings import values
from django.utils.translation import ugettext_lazy as _
from askbot.skins import utils as skin_utils
from askbot import const
from askbot.conf.super_groups import CONTENT_AND_UI

VOCALBULARY = ConfigurationGroup(
                    'VOCALBULARY',
                    _('Site term vocalbulary'),
                    super_group = CONTENT_AND_UI
                )

settings.register(
    values.StringValue(
        VOCALBULARY,
        'ASK_BUTTON_TEXT',
        default = '',
        description = _('Ask new question button'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'ASK_GROUP_BUTTON_TEXT',
        default = '',
        description = _('Ask new question to group button'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'ANSWER_BUTTON_TEXT',
        default = '',
        description = _('Post answer button'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'ANSWER_OWN_QUESTION_BUTTON_TEXT',
        default = '',
        description = _('Answer your own question button'),
    )
)

#settings.register(
#    values.StringValue(
#        VOCALBULARY,
#        'EDIT_QUESTION_BUTTON_TEXT',
#        default = '',
#        description = _('Edit Question button text'),
#    )
#)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'EDIT_ANSWER_BUTTON_TEXT',
        default = '',
        description = _('Edit answer button'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'QUESTION_SINGULAR',
        default = '',
        description = _('question (singular)'),
        help_text = _('Replace Questions word in the site, default text: "question"'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'QUESTION_PLURAL',
        default = '',
        description = _('questions (plural)'),
        help_text = _('Replace Questions word in the site, default text: "questions"'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_SHOW_ONLY_QUESTIONS_FROM',
        default = '',
        description = _('Phrase: Show only questions from'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_PLEASE_ASK_YOUR_QUESTION_HERE',
        default = '',
        description = _('Phrase: Please ask your question here'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_PLEASE_ENTER_YOUR_QUESTION',
        default = '',
        description = _('Phrase: Please enter your question'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_ASK_A_QUESTION_INTERESTING_TO_THIS_COMMUNITY',
        default = '',
        description = _('Phrase: ask a question interesting to this community'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_ASK_YOUR_QUESTION',
        default = '',
        description = _('Phrase: Ask your question!'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_NO_QUESTIONS_HERE',
        default = '',
        description = _('Phrase: No questions here'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_PLEASE_FOLLOW_QUESTIONS',
        default = '',
        description = _('Phrase: Please follow some questions or follow some users.'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_PLEASE_FEEL_FREE_TO_ASK_YOUR_QUESTION',
        default = '',
        description = _('Phrase: Please feel free to ask your question!.'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_SWAP_WITH_QUESTION',
        default = '',
        description = _('Phrase: swap with question.'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_REPOST_AS_A_QUESTION_COMMENT',
        default = '',
        description = _('Phrase: repost as a question comment.'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_THE_QUESTION_HAS_BEEN_CLOSED_FOR_THE_FOLLOWING_REASON',
        default = '',
        description = _('Phrase: the question has been closed for the following reason'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_INVITE_OTHERS_TO_HELP_ANSWER_THIS_QUESTION',
        default = '',
        description = _('Phrase: invite other to help answer this question'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_RELATED_QUESTIONS',
        default = '',
        description = _('Phrase: Related questions'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_QUESTION_TOOLS',
        default = '',
        description = _('Phrase: Question Tools'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_THIS_QUESTION_IS_CURRENTLY_SHARED_ONLY_WITH',
        default = '',
        description = _('Phrase: this question is currently shared only with:'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_BE_THE_FIRST_TO_ANSWER_THIS_QUESTION',
        default = '',
        description = _('Phrase: Be the first to answer this question!'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_FOLLOWED_QUESTIONS',
        default = '',
        description = _('Phrase: followed questions'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_COMMENTS_AND_ANSWERS_TO_OTHERS_QUESTIONS',
        default = '',
        description = _('Phrase: comments and answers to others questions'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_QUESTIONS_THAT_THE_USER_IS_FOLLOWING',
        default = '',
        description = _('Phrase: questions that the user is follwing'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_YOU_CAN_POST_QUESTIONS_BY_EMAILING_THEM_AT',
        default = '',
        description = _('Phrase: You can post questions by emailing them at'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_ASK_A_QUESTION',
        default = '',
        description = _('Phrase: Ask a question'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_LIST_OF_QUESTIONS',
        default = '',
        description = _('Phrase: List of questions'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_THIS_QUESTION_OR_ANSWER_HAS_BEEN_DELETED',
        default = '',
        description = _('Phrase: This question or answer has been deleted'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_SEE_ALL_QUESTIONS',
        default = '',
        description = _('Phrase: See all questions'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_TRY_TO_MAKE_YOUR_QUESTION_INTERESTING',
        default = '',
        description = _('Phrase: please, try to make your question interesting to this community'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_COMMUNITY_GIVES_YOU_AWARDS',
        default = '',
        description = _('Phrase: Community gives you awards for your questions, asnwers and votes'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_CLOSE_QUESTION',
        default = '',
        description = _('Phrase: Close question'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_EDIT_QUESTION',
        default = '',
        description = _('Phrase: Edit question'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_QUESTION_IN_ONE_SENTENCE',
        default = '',
        description = _('Phrase: Question - in one sentence'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_RETAG_QUESTION',
        default = '',
        description = _('Phrase: Retag question'),
    )
)

settings.register(
    values.StringValue(
        VOCALBULARY,
        'WORDS_REOPEN_QUESTION',
        default = '',
        description = _('Phrase: Reopen question'),
    )
)
