from django.http import HttpResponseRedirect
class CancelActionMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # TODO: remove this middleware
        return None
