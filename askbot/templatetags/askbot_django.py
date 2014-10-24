from django import template
from django.core.urlresolvers import reverse
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.safestring import mark_safe

from askbot.conf import settings as askbot_settings
from askbot.utils.pluralization import py_pluralize as _py_pluralize
from askbot.utils import functions
from askbot.search.state_manager import SearchState
from askbot.utils.slug import slugify

register = template.Library()

@register.filter
def as_js_bool(some_object):
    if bool(some_object):
        return 'true'
    return 'false'

@register.filter
def set_sort_method(search_state, sort_method):
    """sets sort method on search state"""
    return search_state.change_sort(sort_method)

@register.filter
def remove_author(search_state):
    return search_state.remove_author()

@register.filter
def remove_tags(search_state):
    return search_state.remove_tags()

@register.filter
def add_tag(search_state, tag):
    return search_state.add_tag(tag)

@register.filter
def change_page(search_state, page):
    return search_state.change_page(page)

@register.filter
def change_scope(search_state, scope):
    return search_state.change_scope(scope)

@register.filter
def get_url(search_state):
    return mark_safe(search_state.full_url())

@register.filter
def full_ask_url(search_state):
    return mark_safe(search_state.full_ask_url())

@register.filter
def get_answer_count(thread, visitor):
    return thread.get_answer_count(visitor)

@register.filter
def get_value(obj, key):
    return obj[key]

@register.filter
def trim(text):
    return text.strip()

@register.filter
def get_latest_revision(thread, visitor):
    return thread.get_latest_revision(visitor)

@register.filter
def render_asterisk(text):
    return text.replace('*', '&#10045;')

@register.filter
def remove_dots(text):
    return text.replace('.', '')

@register.filter
def endswith(text, what):
    return text.endswith(what)

setup_paginator = register.filter(functions.setup_paginator)

@register.filter
def reverse(iterable):
    return reversed(iterable)

@register.filter
def tag_used_count(count):
    return '<span class="tag-number">&#215; %s</span>' % intcomma(count)

@register.filter
def get_avatar_url(user):
    return user.get_avatar_url()

@register.filter
def question_absolute_url(question, thread):
    return question.get_absolute_url(thread=thread)

@register.filter
def show_block_to(block_name, user):
    block = getattr(askbot_settings, block_name)
    if block:
        flag_name = block_name + '_ANON_ONLY'
        require_anon = getattr(askbot_settings, flag_name, False)
        return (require_anon is False) or user.is_anonymous()
    return False

@register.filter
def py_pluralize(source, count):
    plural_forms = source.strip().split('\n')
    return _py_pluralize(plural_forms, count)

class ThreadSummaryNode(template.Node):
    def __init__(self, thread_token, search_state_token, visitor_token):
        self.thread = template.Variable(thread_token)
        self.search_state = template.Variable(search_state_token)
        self.visitor = template.Variable(visitor_token)

    def render(self, context):
        thread = self.thread.resolve(context)
        search_state = self.search_state.resolve(context)
        visitor = self.visitor.resolve(context)
        return thread.get_summary_html(search_state, visitor)

@register.tag
def thread_summary_html(thread, tokens): 
    tag_name, thread_token, search_state_token, visitor_token = tokens.split_contents()
    return ThreadSummaryNode(thread_token, search_state_token, visitor_token)

@register.inclusion_tag('widgets/avatar.html')
def avatar(user, size):
    return {'user': user, 'size': size}

@register.inclusion_tag('widgets/tag_list.html')
def tag_list_widget(tags, **kwargs):
    kwargs['tags'] = tags
    kwargs.setdefault('tag_html_tag', 'li')
    kwargs.setdefault('make_links', True)
    return kwargs

@register.inclusion_tag('widgets/tag.html')
def tag_widget(tag, **kwargs):
    kwargs['tag'] = tag
    kwargs.setdefault('html_tag', 'div')
    kwargs.setdefault('is_link', True)
    if kwargs.get('search_state') is None:
        kwargs['search_state'] = SearchState.get_empty()
    return kwargs

@register.inclusion_tag('widgets/radio_select.html')
def radio_select(name=None, value=None, choices=None):
    choices_data = list()
    for choice in choices:
        choice_datum = {
            'id': 'id_%s_%s' % (name, choice[0]),
            'value': choice[0],
            'label': choice[1]
        }
        choices_data.append(choice_datum)
    return {
        'name': name,
        'value': value,
        'choices': choices_data
    }

@register.inclusion_tag('widgets/tag_cloud.html')
def tag_cloud(tags=None, font_sizes=None, search_state=None):
    tags_data = list()
    for tag in tags:
        tag_datum = {
            'name': tag.name,
            'font_size': font_sizes[tag.name]
        }
        tags_data.append(tag_datum)
    return {
        'tags': tags_data,
        'search_state': search_state
    }

@register.inclusion_tag('widgets/user_country_flag.html')
def user_country_flag(user):
    context = {
        'user': user,
    }
    if user.country and user.show_counry:
        context['flag_url'] = '/images/flags/' + user.country.code.lower() + '.gif'
    return context

@register.inclusion_tag('widgets/user_primary_group.html')
def user_primary_group(user):
    group = user.get_primary_group()    
    group_name = group.name.replace('-', ' ')
    group_url = reverse('users_by_group', args=(group.id, slugify(group_name)))
    return {
        'group_name': group_name,
        'group_url': group_url
    }

@register.inclusion_tag('widgets/reversible_sort_button.html')
def reversible_sort_button(**kwargs):
    key_name = kwargs['key_name']
    kwargs['key_name_asc'] = key_name + '-asc'
    kwargs['key_name_desc'] = key_name + '-desc'
    return kwargs
