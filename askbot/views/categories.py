from askbot.skins.loaders import render_into_skin

def widget(request):
    return render_into_skin('categories_widget.html', {}, request)
