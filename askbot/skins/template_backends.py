from django.template.backends.base import BaseEngine
from askbot.skins.loaders import Loader, get_skin

class AskbotSkinTemplates(BaseEngine):

    def __init__(self, params):
        junk = params.pop('OPTIONS') #we don't use this parameter
        super(AskbotSkinTemplates, self).__init__(params)
        self.loader = Loader(self)

    def get_template(self, name):
        return Template(self.loader.load_template(name)[0])

    def from_string(self, template_code):
        skin = get_skin()
        return Template(skin.from_string(template_code))


class Template(object):

    def __init__(self, template):
        self.template = template

    def render(self, context=None, request=None):
        if context is None:
            context = {}
        if request is not None:
            context['request'] = request
        return self.template.render(context)
