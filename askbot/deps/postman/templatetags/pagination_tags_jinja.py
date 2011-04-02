"""
A mock of django-pagination's pagination_tags.py that do nothing.
Just to avoid failures in template rendering during the test suite,
if the real application is not installed.

To activate this mock, just rename it to ``pagination_tags.py``
for the time of the test session.
"""
from django.template import Node, Library
from coffin import template as coffin_template
from jinja2.ext import Extension

register = coffin_template.Library()

class AutoPaginateNode(Node):
    def render(self, context):
        return u''

@register.filter
def autopaginate(token):
    return u'' 

class PaginateNode(Node):
    def render(self, context):
        return u''

def paginate(parser, token):
    return PaginateNode()

@register.tag
class PaginateExtention(Extension):
    tags = ['paginate']
    def __init__(self, enviroment):
        pass

    def parse(self, parser):
        return u''
