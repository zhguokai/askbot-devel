from categories.models import Category

from askbot.skins.loaders import render_into_skin

def cats(request):
    return render_into_skin('categories.html', {}, request)
