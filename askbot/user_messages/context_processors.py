"""
Context processor for lightweight session messages.

Time-stamp: <2008-07-19 23:16:19 carljm context_processors.py>

"""
from django.conf import settings as django_settings
from django.contrib import messages as django_messages
from django.utils.encoding import StrAndUnicode

from askbot.user_messages import get_and_delete_messages

def user_messages(request):
    """
    Returns session messages for the current session.

    """
    #don't delete messages on ajax requests b/c we can't show
    #them the same way as in the server side generated html
    if request.is_ajax():
        return {}
    if not request.path.startswith('/' + django_settings.ASKBOT_URL):
        #todo: a hack, for real we need to remove this middleware
        #and switch to the new-style session messages
        return {}

    if hasattr(request.user, 'get_and_delete_messages'):
        messages = request.user.get_and_delete_messages()
        messages += django_messages.get_messages(request)
        return { 'user_messages': messages }
    else:
        return { 'user_messages': django_messages.get_messages(request) }
