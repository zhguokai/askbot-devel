from django.middleware.csrf import CsrfViewMiddleware as DjangoCsrfViewMiddleware
from django.middleware.csrf import get_token
from django.middleware import csrf

def get_or_create_csrf_token(request):
    token = request.META.get('CSRF_COOKIE', None)
    if token is None:
        token = csrf._get_new_csrf_key()
        request.META['CSRF_COOKIE'] = token
        request.META['CSRF_COOKIE_USED'] = True
        return token

class CsrfViewMiddleware(object):
    """we use this middleware to set csrf token to
    every response, because modal menues that post
    need this token"""
    def __init__(self, *args, **kwargs):
        self._instance = DjangoCsrfViewMiddleware(*args, **kwargs)

    def process_response(self, request, response):
        """will set csrf cookie to all responses"""
        #these two calls make the csrf token cookie to be installed
        #properly on the response, see implementation of those calls
        #to see why this works and why get_token is necessary
        get_token(request)
        return self._instance.process_response(request, response)
