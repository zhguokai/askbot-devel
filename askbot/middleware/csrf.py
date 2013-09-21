from django.middleware.csrf import CsrfViewMiddleware as DjangoCsrfViewMiddleware

class CsrfViewMiddleware(object):
    """we use this middleware to set csrf token to
    every response, because modal menues that post
    need this token"""
    def __init__(self, *args, **kwargs):
        self._instance = DjangoCsrfViewMiddleware(*args, **kwargs)

    def process_response(self, request, response):
        """will set csrf cookie to all responses"""
        return self._instance.process_response(request, response)
