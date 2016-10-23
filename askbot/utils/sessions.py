def set_referrer_as_savepoint_url(request, sticky=False):
    from askbot.utils.http import get_referrer_url
    url = get_referrer_url(request)
    set_savepoint_url(request, url, sticky)

def set_savepoint_url(request, url, sticky=False):
    request.session['SAVEPOINT_URL'] = url
    if sticky:
        request.session['SAVEPOINT_URL_STICKY'] = True

def is_savepoint_url_sticky(request):
    return request.session.get('SAVEPOINT_URL_STICKY', False)

def get_savepoint_url(request, default=None):
    if 'SAVEPOINT_URL' in request.session:
        return request.session['SAVEPOINT_URL']
    from askbot.models.spaces import get_feed_url
    return default or get_feed_url('questions')

def delete_savepoint_url(request):
    if 'SAVEPOINT_URL' in request.session:
        del request.session['SAVEPOINT_URL']
    if 'SAVEPOINT_URL_STICKY' in request.session:
        del request.session['SAVEPOINT_URL_STICKY']
