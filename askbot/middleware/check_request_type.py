from django.http import HttpResponseNotAllowed

class CheckRequestTypeMiddleware(object):
    def process_request(self, request):
        if request.method == 'OPTIONS':
            return HttpResponseNotAllowed(request)
        return None
