from django.utils import translation
from django.conf import settings
from localeurl.middleware import LocaleURLMiddleware

class JinjaDjangoLocaleUrlMiddleware(LocaleURLMiddleware):
    """subclass of locale url middleware that
    enables support of Jinja2 templates as well as django templates
    """

    def process_request(self, request):
        """calls process_request of LocaleMiddleware
        then finishes the job for jinja2
        """
        response = super(
                    JinjaDjangoLocaleUrlMiddleware,
                    self
                ).process_request(request)

        if response is not None:
            return response

        from askbot.skins.loaders import ENV
        ENV.set_language(request.LANGUAGE_CODE)

    def process_response(self, request, response):
        response = super(
                    JinjaDjangoLocaleUrlMiddleware,
                    self
                ).process_response(request, response)

        from askbot.skins.loaders import ENV
        ENV.set_language(settings.LANGUAGE_CODE)
        return response
