"""
A mock of django-pagination's pagination_tags.py that do nothing.
Just to avoid failures in template rendering during the test suite,
if the real application is not installed.

To activate this mock, just rename it to ``pagination_tags.py``
for the time of the test session.
"""
from django.template import Node, Library
from coffin import template as coffin_template

register = coffin_template.Library()

class AutoPaginateNode(Node):
    def render(self, context):
        return u''

@register.filter
def autopaginate(parser, token):
    return u'' 

class PaginateNode(Node):
    def render(self, context):
        return u''

@register.simple_tag
def paginate(parser, token):
    return PaginateNode()
