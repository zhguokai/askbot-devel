import datetime

from django.http import QueryDict
from django.template.defaultfilters import date
from django.utils.translation import ugettext_lazy as _
from coffin import template as coffin_template

from jinja2.ext import Extension
from jinja2 import nodes
import jinja2

from postman.models import ORDER_BY_MAPPER, ORDER_BY_KEY, Message

register = coffin_template.Library()

##########
# filters
##########

@register.filter
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def or_me(value, arg):
    """
    Replace the value by a fixed pattern, if it equals the argument.

    Typical usage: sender|or_me:user

    """
    if str(value) == str(arg):
        return _('<me>')
    else:
        return value

@register.filter
def compact_date(value, arg):
    """
    Output a date as short as possible.

    The argument must provide 3 patterns: for same day, for same year, otherwise
    Typical usage: |compact_date:_("G:i,j b,j/n/y")

    """
    bits = arg.split(u',')
    if len(bits) < 3:
        return value # Invalid arg.
    today = datetime.date.today()
    return date(value, bits[0] if value.date() == today else bits[1] if value.year == today.year else bits[2])

@register.filter
def unread_count(value, arg=None):
    try:
        user = value
        if user.is_anonymous():
            count = None 
        else:
            count = Message.objects.inbox_unread_count(user)
    except (KeyError, AttributeError):
        count = None 
        return None 

    return count


#######
# tags
#######
@register.tag
class OrderByExtension(Extension):
    tags = set(['postman_order_by'])

    def __init__(self, environment):
        self.code = None
        super(OrderByExtension, self).__init__(environment)

    def parse(self, parser):
        parser.parse_expression()
        try:
            token = parser.stream.next()
            tag_name, field_name = token.type, token.value
            field_code = ORDER_BY_MAPPER[field_name.lower()]
        except ValueError:
            raise TemplateSyntaxError("'{0}' tag requires a single argument".format(token.contents.split()[0]))
        except KeyError:
            raise TemplateSyntaxError(
            "'{0}' is not a valid argument to '{1}' tag."
            " Must be one of: {2}".format(field_name, tag_name, ORDER_BY_MAPPER.keys()))
        
        return nodes.Output([
                self.call_method('_render', [nodes.Const(field_name), nodes.Dict({})]),
                ])

    def _render(self, name, context):
        self.code = name

        if 'gets' in context:
            gets = context['gets'].copy()
        else:
            gets = QueryDict('').copy()
        if ORDER_BY_KEY in gets:
            code = gets.pop(ORDER_BY_KEY)[0]
        else:
            code = None
        if self.code:
            gets[ORDER_BY_KEY] = self.code if self.code <> code else self.code.upper()
        result = '?'+gets.urlencode() if gets else ''
        return jinja2.Markup(result)
        

class InboxCountExtention(Extension):
    '''substitute for the postman_unread tag'''

    def __init__(self, enviroment):
        pass

    def _render(self, context):
        """
        Return the count of unread messages for the user found in context,
        (may be 0) or an empty string.
        """
        try:
            user = context['user']
            if user.is_anonymous():
                count = ''
            else:
                count = Message.objects.inbox_unread_count(user)
        except (KeyError, AttributeError):
            count = ''
        if self.asvar:
            context[self.asvar] = count
            return ''
        return count 
