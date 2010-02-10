from django.conf import settings
from django import template
from django.template import loader, Context
from django.http import HttpResponse
import os.path
import logging

def get_template(name):
    try:
        tpath = os.path.join(settings.OSQA_SKIN,'templates',name)
        t = loader.get_template(os.path.join(settings.OSQA_SKIN,'templates',name))
    except:
        t = loader.get_template(os.path.join('default','templates',name))
    return t

def find_template_source(name, dirs=None):
    try:
        tname = os.path.join(settings.OSQA_SKIN,'templates',name)
        return loader.find_template_source(tname,dirs)
    except:
        tname = os.path.join('default','templates',name)
        return loader.find_template_source(tname,dirs)

def render_to_response(template_name, data={}, context_instance=None):
    t = get_template(template_name)
    if context_instance != None:
        context_instance.update(data)
        context = context_instance
    else:
        context = Context(data)
    return HttpResponse(t.render(context))

class TemplateLibrary(template.Library):
    def inclusion_tag(self,name,*arg,**kwarg):
        try:
            tname = os.path.join(settings.OSQA_SKIN,'templates',name)
            return super(TemplateLibrary, self).inclusion_tag(tname,*arg,**kwarg)
        except:
            tname = os.path.join('default','templates',name)
            return super(TemplateLibrary, self).inclusion_tag(tname,*arg,**kwarg)
