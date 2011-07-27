"""login and logout functions - that should work with or 
without askbot module"""
from django.conf import settings
from django.contrib.auth import logout as django_logout#for login I've added wrapper below - called login
from django.contrib.auth import login as django_login
import logging

#todo: decouple from askbot
def askbot_login(request,user):
    from askbot.models import signals

    #1) get old session key
    session_key = request.session.session_key
    #2) get old search state
    search_state = None
    if 'search_state' in request.session:
        search_state = request.session['search_state']

    #3) login and get new session key
    django_login(request,user)
    #4) transfer search_state to new session if found
    if search_state:
        search_state.set_logged_in()
        request.session['search_state'] = search_state
    #5) send signal with old session key as argument
    logging.debug('logged in user %s with session key %s' % (user.username, session_key))
    #todo: move to auth app
    signals.user_logged_in.send(
        request = request,
        user = user,
        session_key=session_key,
        sender=None
    )

def askbot_logout(request):
    if 'search_state' in request.session:
        request.session['search_state'].set_logged_out()
        request.session.modified = True
    django_logout(request)

if 'askbot' is settings.INSTALLED_APPS:
    login = askbot_login
    logout = askbot_logout
else:
    login = django_login
    logout = django_logout
