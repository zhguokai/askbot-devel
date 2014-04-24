from django.contrib.auth import logout
class LogOutBlockedUserMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and request.user.is_blocked():
            logout(request)
