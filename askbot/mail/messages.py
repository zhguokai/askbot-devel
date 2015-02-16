"""functions in this module return body text
of email messages for various occasions
"""
import functools
import urllib
from django.conf import settings as django_settings
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from askbot import const
from askbot.conf import settings as askbot_settings
from askbot.utils import html as html_utils
from askbot.utils.diff import textDiff as htmldiff
from askbot.utils.html import (sanitize_html, site_url)
from askbot.utils.slug import slugify

def message(template = None):
    """a decorator that creates a function
        which returns formatted message using the
        template and data"""
    def decorate(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            template_object = get_template(template)
            data = func(*args, **kwargs)
            return template_object.render(Context(data))#todo: set lang
        return wrapped
    return decorate

@message(template = 'email/ask_for_signature.html')
def ask_for_signature(user, footer_code = None):
    """tells that we don't have user's signature
    and because of that he/she cannot make posts
    the message will ask to make a simple response
    """
    return {
        'footer_code': footer_code,
            'recipient_user': user,
            'site_name': askbot_settings.APP_SHORT_NAME,
            'username': user.username,
    }

@message(template = 'email/notify_admins_about_new_tags.html')
def notify_admins_about_new_tags(
        tags = None, thread = None, user = None
        ):
    thread_url = thread.get_absolute_url()
    return {
        'thread_url': html_utils.site_url(thread_url),
            'tags': tags,
            'user': user
    }

@message(template = 'email/insufficient_rep_to_post_by_email.html')
def insufficient_reputation(user):
    """tells user that he does not have
    enough rep and suggests to ask on the web
    """
    min_rep = askbot_settings.MIN_REP_TO_POST_BY_EMAIL
    min_upvotes = 1 + \
                  (min_rep/askbot_settings.REP_GAIN_FOR_RECEIVING_UPVOTE)
    site_link = html_utils.site_link(
            'ask',
            askbot_settings.APP_SHORT_NAME
            )
    return {
        'username': user.username,
        'site_name': askbot_settings.APP_SHORT_NAME,
        'site_link': site_link,
        'min_upvotes': min_upvotes
    }

class BaseEmail(object):
    """Base class for templated emails.

    Besides sending formatted emails,
    this class allows to generate 
    email mockups, to help development
    of the email templates.

    Subclass must specify variables:
    * `template_path` - path to the directory which must contain
       files `subject.txt` and `body.txt`
    * `title` - a brief title for this email
    * `description` - string explaining why/when this email is sent
    * `mock_context` - optional, may be replaced with custom method
    get_mock_context(), see below

    plain text version of the email is calculated from body.html
    by stripping tags
    """

    template_path = 'path/to/email/dir' #override in subclass
    title = 'A brief title for this email'
    description = 'In subclass, explain when/why this email might be sent'
    mock_context = {}

    def __init__(self, context=None):
        self.context = context
        self._cached_context = None

    def process_context(self, context):
        """override if context requires post-processing"""
        return context

    def get_attachments(self):
        """override if attachments need to be determined from context"""
        return None

    def get_mock_context(self):
        """override if need to fetch mock context dynamically"""
        return self.mock_context

    def get_context(self):
        if self._cached_context:
            return self._cached_context
        context = self.context or self.get_mock_context() or self.mock_context
        self._cached_context = self.process_context(context)
        return Context(self._cached_context)

    def get_headers(self):
        """override this method if headers need to be calculated
        from context"""
        return None

    def render_subject(self):
        template = get_template(self.template_path + '/subject.txt')
        return template.render(self.get_context())

    def render_body(self):
        template = get_template(self.template_path + '/body.html')
        return template.render(self.get_context())

    def send(self, recipient_list, raise_on_failure=False, headers=None, attachments=None):
        from askbot.mail import send_mail
        send_mail(
            subject_line=self.render_subject(),
            body_text=self.render_body(),
            from_email=None,
            recipient_list=recipient_list,
            headers=headers or self.get_headers(),
            raise_on_failure=raise_on_failure,
            attachments=attachments or self.get_attachments()
        )

class InstantEmailAlert(BaseEmail):
    template_path = 'email/instant_notification'
    title = _('Instant email notification')
    description = _('Sent to relevant users when a post is made or edited')
    preview_error_message = _(
        'At least two users and one post are needed to generate the preview'
    )

    def get_mock_context(self):
        from askbot.models import (Activity, Post, User)
        post_types = ('question', 'answer', 'comment')
        post = Post.objects.filter(post_type__in=post_types)[0]

        if post.is_question():
            activity_type = const.TYPE_ACTIVITY_ASK_QUESTION
        elif post.is_answer():
            activity_type = const.TYPE_ACTIVITY_ANSWER
        elif post.parent.is_question():
            activity_type = const.TYPE_ACTIVITY_COMMENT_QUESTION
        else:
            activity_type = const.TYPE_ACTIVITY_COMMENT_ANSWER

        activity = Activity(
                    user=post.author,
                    content_object=post,
                    activity_type=activity_type,
                    question=post.get_origin_post()
                )
        return {
            'post': post,
            'from_user': post.author,
            'to_user': User.objects.exclude(id=post.author_id)[0],
            'update_activity': activity
        }

    def get_headers(self):
        context = self.get_context()
        post = context['post']
        origin_post = context['origin_post']
        reply_address = context['reply_address']
        update_activity = context['update_activity']

        headers = self.get_thread_headers(
            post,
            origin_post,
            update_activity.activity_type
            )
        headers['Reply-To'] = reply_address
        return headers

    def get_thread_headers(self, post, orig_post, update):
        """modify headers for email messages, so
        that emails appear as threaded conversations in gmail"""
        suffix_id = django_settings.SERVER_EMAIL
        if update == const.TYPE_ACTIVITY_ASK_QUESTION:
            msg_id = "NQ-%s-%s" % (post.id, suffix_id)
            headers = {'Message-ID': msg_id}
        elif update == const.TYPE_ACTIVITY_ANSWER:
            msg_id = "NA-%s-%s" % (post.id, suffix_id)
            orig_id = "NQ-%s-%s" % (orig_post.id, suffix_id)
            headers = {'Message-ID': msg_id, 'In-Reply-To': orig_id}
        elif update == const.TYPE_ACTIVITY_UPDATE_QUESTION:
            msg_id = "UQ-%s-%s-%s" % (post.id, post.last_edited_at, suffix_id)
            orig_id = "NQ-%s-%s" % (orig_post.id, suffix_id)
            headers = {'Message-ID': msg_id, 'In-Reply-To': orig_id}
        elif update == const.TYPE_ACTIVITY_COMMENT_QUESTION:
            msg_id = "CQ-%s-%s" % (post.id, suffix_id)
            orig_id = "NQ-%s-%s" % (orig_post.id, suffix_id)
            headers = {'Message-ID': msg_id, 'In-Reply-To': orig_id}
        elif update == const.TYPE_ACTIVITY_UPDATE_ANSWER:
            msg_id = "UA-%s-%s-%s" % (post.id, post.last_edited_at, suffix_id)
            orig_id = "NQ-%s-%s" % (orig_post.id, suffix_id)
            headers = {'Message-ID': msg_id, 'In-Reply-To': orig_id}
        elif update == const.TYPE_ACTIVITY_COMMENT_ANSWER:
            msg_id = "CA-%s-%s" % (post.id, suffix_id)
            orig_id = "NQ-%s-%s" % (orig_post.id, suffix_id)
            headers = {'Message-ID': msg_id, 'In-Reply-To': orig_id}
        else:
            # Unknown type -> Can't set headers
            return {}
        return headers

    @classmethod
    def get_update_type(cls, activity):
        update_type_map = const.RESPONSE_ACTIVITY_TYPE_MAP_FOR_TEMPLATES
        return update_type_map[activity.activity_type]

    def process_context(self, context):
        to_user = context.get('to_user')
        from_user = context.get('from_user')
        post = context.get('post')
        update_activity = context.get('update_activity')
        update_type = self.get_update_type(update_activity)

        origin_post = post.get_origin_post()

        from askbot.models import Post
        if update_type == 'question_comment':
            assert(isinstance(post, Post) and post.is_comment())
            assert(post.parent and post.parent.is_question())
        elif update_type == 'answer_comment':
            assert(isinstance(post, Post) and post.is_comment())
            assert(post.parent and post.parent.is_answer())
        elif update_type == 'answer_update':
            assert(isinstance(post, Post) and post.is_answer())
        elif update_type == 'new_answer':
            assert(isinstance(post, Post) and post.is_answer())
        elif update_type == 'question_update':
            assert(isinstance(post, Post) and post.is_question())
        elif update_type == 'new_question':
            assert(isinstance(post, Post) and post.is_question())
        elif update_type == 'post_shared':
            pass
        else:
            raise ValueError('unexpected update_type %s' % update_type)

        if update_type.endswith('update'):
            assert('comment' not in update_type)
            revisions = post.revisions.all()[:2]
            assert(len(revisions) == 2)
            content_preview = htmldiff(
                    sanitize_html(revisions[1].html),
                    sanitize_html(revisions[0].html),
                    ins_start = '<b><u style="background-color:#cfc">',
                    ins_end = '</u></b>',
                    del_start = '<del style="color:#600;background-color:#fcc">',
                    del_end = '</del>'
                )
            #todo: remove hardcoded style
        else:
            content_preview = post.format_for_email(is_leaf_post=True, recipient=to_user)

        #add indented summaries for the parent posts
        content_preview += post.format_for_email_as_parent_thread_summary(recipient=to_user)

        #content_preview += '<p>======= Full thread summary =======</p>'
        #content_preview += post.thread.format_for_email(recipient=to_user)

        if update_type == 'post_shared':
            user_action = _('%(user)s shared a %(post_link)s.')
        elif post.is_comment():
            if update_type.endswith('update'):
                user_action = _('%(user)s edited a %(post_link)s.')
            else:
                user_action = _('%(user)s posted a %(post_link)s')
        elif post.is_answer():
            if update_type.endswith('update'):
                user_action = _('%(user)s edited an %(post_link)s.')
            else:
                user_action = _('%(user)s posted an %(post_link)s.')
        elif post.is_question():
            if update_type.endswith('update'):
                user_action = _('%(user)s edited a %(post_link)s.')
            else:
                user_action = _('%(user)s posted a %(post_link)s.')
        else:
            raise ValueError('unrecognized post type')

        post_url = site_url(post.get_absolute_url())
        user_url = site_url(from_user.get_absolute_url())

        if to_user.is_administrator_or_moderator() and askbot_settings.SHOW_ADMINS_PRIVATE_USER_DATA:
            user_link_fmt = '<a href="%(profile_url)s">%(username)s</a> (<a href="mailto:%(email)s">%(email)s</a>)'
            user_link = user_link_fmt % {
                'profile_url': user_url,
                    'username': from_user.username,
                    'email': from_user.email
            }
        elif post.is_anonymous:
            user_link = from_user.get_name_of_anonymous_user()
        else:
            user_link = '<a href="%s">%s</a>' % (user_url, from_user.username)

        user_action = user_action % {
            'user': user_link,
            'post_link': '<a href="%s">%s</a>' % (post_url, _(post.post_type))
        }

        can_reply = to_user.can_post_by_email()
        from askbot.models import get_reply_to_addresses
        reply_address, alt_reply_address = get_reply_to_addresses(to_user, post)

        if can_reply:
            reply_separator = const.SIMPLE_REPLY_SEPARATOR_TEMPLATE % \
                          _('To reply, PLEASE WRITE ABOVE THIS LINE.')
            if post.post_type == 'question' and alt_reply_address:
                data = {
                  'addr': alt_reply_address,
                  'subject': urllib.quote(
                            ('Re: ' + post.thread.title).encode('utf-8')
                          )
                }
                reply_separator += '<p>' + const.REPLY_WITH_COMMENT_TEMPLATE % data
                reply_separator += '</p>'
            else:
                reply_separator = '<p>%s</p>' % reply_separator
                reply_separator += user_action
        else:
            reply_separator = user_action

        user_subscriptions_url = reverse('user_subscriptions',
                                       kwargs={
                                           'id': to_user.id,
                                           'slug': slugify(to_user.username)
                                       }
                                    )
        return {
           'admin_email': askbot_settings.ADMIN_EMAIL,
           'recipient_user': to_user,
           'update_author_name': from_user.username,
           'receiving_user_name': to_user.username,
           'receiving_user_karma': to_user.reputation,
           'reply_by_email_karma_threshold': askbot_settings.MIN_REP_TO_POST_BY_EMAIL,
           'can_reply': can_reply,
           'content_preview': content_preview,
           'update_type': update_type,
           'update_activity': update_activity,
           'post': post,
           'post_url': post_url,
           'origin_post': origin_post,
           'thread_title': origin_post.thread.title,
           'user_subscriptions_url': site_url(user_subscriptions_url),
           'reply_separator': reply_separator,
           'reply_address': reply_address,
           'is_multilingual': getattr(django_settings, 'ASKBOT_MULTILINGUAL', False)
        }
