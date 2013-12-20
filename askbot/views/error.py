from django.shortcuts import render

def internal_error(request):
    data = {}
    try:
        from askbot.conf import settings as askbot_settings
        data['settings'] = askbot_settings
    except Exception:
        data['settings'] = {}
    return render(request, '500.html', data)
