from django.middleware.csrf import CsrfViewMiddleware as DjangoCsrfViewMiddleware
from django.middleware.csrf import get_token
from django.middleware import csrf

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
