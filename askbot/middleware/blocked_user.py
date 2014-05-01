from askbot.conf import settings as askbot_settings
from django.contrib.auth import logout
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def get_blocked_message():
    return askbot_settings.BLOCKED_USER_LOGIN_MESSAGE

class LogOutBlockedUserMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and request.user.is_blocked():
            logout(request)
            messages.add_message(request, messages.INFO, get_blocked_message())

    def process_response(self, request, response):
        if request.user.is_authenticated() and request.user.is_blocked():
            logout(request)
            messages.add_message(request, messages.INFO, get_blocked_message())
            return HttpResponseRedirect(reverse('index'))
        return response
