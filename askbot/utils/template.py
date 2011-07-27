"""template adapter module
"""
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import get_template as django_get_template

def render_template(template_name, data, request, mimetype = 'text/html'):
    """an adatpter function that allows to render template either
    into askbot skin or simply the django way, if askbot module is 
    not installed.

    Note that askbot templates are all written for Jinja2, not
    the django templating engine

    ``template_name`` - path to the template
    ``data`` is template context - a plain dictionary
    ``request`` is django request object
    """
    if 'askbot' in settings.INSTALLED_APPS:
        from askbot.skins.loaders import render_into_skin
        return render_into_skin(
            template_name,
            data,
            request,
            mimetype = mimetype
        )
    else:
        context = RequestContext(request, data)
        return render_to_response(
            template_name,
            context_instance = context,
            mimetype = mimetype
        )

def get_template(template_name, request = None):
    if 'askbot' in settings.INSTALLED_APPS:
        from askbot.skins.loaders import get_template
        return get_template(template_name, request)
    else:
        return django_get_template(template_name)
