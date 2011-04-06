from django.http import HttpResponse
from django.views.generic.simple import direct_to_template


def widget(request):
    #return HttpResponse(u'Hello world from the widget view.')
    return direct_to_template(request, template='categories_widget.html')
