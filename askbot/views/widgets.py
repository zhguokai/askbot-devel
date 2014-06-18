from datetime import datetime

from django.template import RequestContext
from django.template.loader import get_template
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.decorators import csrf
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404

from django.contrib.auth.decorators import login_required

from askbot.conf import settings as askbot_settings
from askbot.utils import decorators
from askbot import models
from askbot.models import signals
from askbot import forms

WIDGETS_MODELS = {
                  'ask': models.AskWidget,
                  'question': models.QuestionWidget
                 }

WIDGETS_FORMS = {
                'ask': forms.CreateAskWidgetForm,
                'question': forms.CreateQuestionWidgetForm,
               }

def _get_model(key):
    '''like get_object_or_404 but for our models'''
    try:
        return WIDGETS_MODELS[key]
    except KeyError:
        raise Http404

def _get_form(key):
    '''like get_object_or_404 but for our forms'''
    try:
        return WIDGETS_FORMS[key]
    except KeyError:
        raise Http404

@decorators.admins_only
def widgets(request):
    data = {
        'ask_widgets': models.AskWidget.objects.all().count(),
        'question_widgets': models.QuestionWidget.objects.all().count(),
        'page_class': 'widgets'
    }
    return render(request, 'embed/widgets.html', data)

@csrf.csrf_protect
def ask_widget(request, widget_id):

    widget = get_object_or_404(models.AskWidget, id=widget_id)

    if request.method == "POST":

        if askbot_settings.READ_ONLY_MODE_ENABLED:
            return redirect('ask_by_widget')

        form = forms.AskWidgetForm(
                    include_text=widget.include_text_field,
                    data=request.POST,
                    user=request.user
                )
        if form.is_valid():
            ask_anonymously = form.cleaned_data['ask_anonymously']
            title = form.cleaned_data['title']
            if widget.include_text_field:
                text = form.cleaned_data['text']
            else:
                text = ' '


            if widget.group:
                group_id = widget.group.id
            else:
                group_id = None

            if widget.tag:
                tagnames = widget.tag.name
            else:
                tagnames = ''

            data_dict = {
                'title': title,
                'body_text': text,
                'space': form.cleaned_data['space'],
                'tags': tagnames,
                'wiki': False,
                'is_anonymous': ask_anonymously,
                'timestamp': datetime.now(),
                'group_id': group_id
            }

            if request.user.is_authenticated():
                question = request.user.post_question(**data_dict)
                request.session['widget_thread_id'] = question.thread.id
                request.session['widget_id'] = widget_id
                signals.new_question_posted.send(None,
                    question=question,
                    user=request.user,
                    form_data=form.cleaned_data
                )
                return redirect('ask_by_widget_complete')
            else:
                request.session['widget_question'] = data_dict
                next_url = '%s?next=%s' % (
                        reverse('widget_signin'),
                        reverse('ask_by_widget', kwargs={'widget_id': widget_id})
                )
                return redirect(next_url)
    else:
        if 'widget_question' in request.session:
            if request.user.is_authenticated():
                data_dict = request.session['widget_question']
                question = request.user.post_question(**data_dict)
                request.session['widget_thread_id'] = question.thread.id
                request.session['widget_id'] = widget_id
                #signals.new_question_posted.send(None,
                #    question=question,
                #    user=request.user,
                #    form_data=data_dict
                #)
                del request.session['widget_question']
                return redirect('ask_by_widget_complete')
            else:
                #FIXME: this redirect is temporal need to create the correct view
                next_url = '%s?next=%s' % (
                    reverse('widget_signin'),
                    reverse('ask_by_widget', kwargs={'widget_id': widget_id})
                )
                return redirect(next_url)

        form = forms.AskWidgetForm(
            include_text=widget.include_text_field,
            user=request.user
        )

    data = {
            'form': form,
            'widget': widget,
            'editor_type': askbot_settings.EDITOR_TYPE
           }
    return render(request, 'embed/ask_by_widget.html', data)

@login_required
def ask_widget_complete(request):
    thread_id = request.session.pop('widget_thread_id')
    thread = models.Thread.objects.get(id=thread_id)
    data = {
        'question_url': thread.get_absolute_url(),
        'question_title': thread.title,
        'question_body_html': thread._question_post().html,
        'custom_css': request.session.pop('widget_css', ''),
        'widget_id': request.session.pop('widget_id')
    }
    return render(request, 'embed/ask_widget_complete.html', data)


@decorators.admins_only
def list_widgets(request, model):
    model_class = _get_model(model)
    widgets = model_class.objects.all()
    data = {
            'widgets': widgets,
            'widget_name': model
           }
    return render(request, 'embed/list_widgets.html', data)

@decorators.admins_only
@csrf.csrf_protect
def create_widget(request, model):
    form_class = _get_form(model)
    model_class = _get_model(model)
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            instance = model_class(**form.cleaned_data)
            instance.save()
            return redirect('list_widgets', model=model)
    else:
        form = form_class()

    data = {'form': form,
            'action': 'edit',
            'widget_name': model}
    return render(request, 'embed/widget_form.html', data)

@decorators.admins_only
@csrf.csrf_protect
def edit_widget(request, model, widget_id):
    model_class = _get_model(model)
    form_class = _get_form(model)
    widget = get_object_or_404(model_class, pk=widget_id)
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form_dict = dict.copy(form.cleaned_data)
            for key in widget.__dict__:
                if key.endswith('_id'):
                    form_key = key.split('_id')[0]
                    if form_dict[form_key]:
                        form_dict[key] = form_dict[form_key].id
                    del form_dict[form_key]
                else:
                    continue

            widget.__dict__.update(form_dict)
            widget.save()
            return redirect('list_widgets', model=model)
    else:
        initial_dict = dict.copy(widget.__dict__)
        for key in initial_dict:
            if key.endswith('_id'):
                new_key = key.split('_id')[0]
                initial_dict[new_key] = initial_dict[key]
                del initial_dict[key]
            else:
                continue

        del initial_dict['_state']
        form = form_class(initial=initial_dict)

    data = {'form': form,
            'action': 'edit',
            'widget_name': model}
    return render(request, 'embed/widget_form.html', data)

@decorators.admins_only
@csrf.csrf_protect
def delete_widget(request, model, widget_id):
    model_class = _get_model(model)
    widget = get_object_or_404(model_class, pk=widget_id)
    if request.method == "POST":
        widget.delete()
        return redirect('list_widgets', model=model)
    else:
        return render(
            request,
            'embed/delete_widget.html',
            {'widget': widget, 'widget_name': model}
        )

def render_ask_widget_js(request, widget_id):
    widget = get_object_or_404(models.AskWidget, pk=widget_id)
    variable_name = "AskbotAskWidget%d" % widget.id
    content_tpl = get_template('embed/askbot_widget.js')
    context_dict = {
        'widget': widget,
        'host': request.get_host(),
        'variable_name': variable_name
    }
    content =  content_tpl.render(RequestContext(request, context_dict))
    return HttpResponse(content, content_type='text/javascript')

def render_ask_widget_css(request, widget_id):
    widget = get_object_or_404(models.AskWidget, pk=widget_id)
    variable_name = "AskbotAskWidget%d" % widget.id
    content_tpl = get_template('embed/askbot_widget.css')
    context_dict = {
        'widget': widget,
        'host': request.get_host(),
        'editor_type': askbot_settings.EDITOR_TYPE,
        'variable_name': variable_name
    }
    content =  content_tpl.render(RequestContext(request, context_dict))
    return HttpResponse(content, content_type='text/css')

def question_widget(request, widget_id):
    """Returns the first x questions based on certain tags.
    @returns template with those questions listed."""
    # make sure this is a GET request with the correct parameters.
    widget = get_object_or_404(models.QuestionWidget, pk=widget_id)

    if request.method != 'GET':
        raise Http404

    filter_params = {}

    if widget.tagnames:
        filter_params['tags__name__in'] = widget.tagnames.split(' ')

    if widget.group:
        filter_params['groups'] = widget.group

    #simple title search for now
    if widget.search_query:
        filter_params['title__icontains'] = widget.search_query

    if filter_params:
        threads = models.Thread.objects.filter(**filter_params).order_by(widget.order_by)[:widget.question_number]
    else:
        threads = models.Thread.objects.all().order_by(widget.order_by)[:widget.question_number]

    data = {
             'threads': threads,
             'widget': widget
           }

    return render(request, 'embed/question_widget.html', data)
