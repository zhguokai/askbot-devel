from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.utils import simplejson
from django.db.models import Q
from django.core.urlresolvers import reverse

from askbot import models
from askbot.conf import settings as askbot_settings
from askbot.search.state_manager import SearchState

def api_forum_info(request):
    '''
       Returns general data about the forum
    '''
    data = {}
    data['answers'] = models.Post.objects.get_answers().count()
    data['questions'] = models.Post.objects.get_questions().count()
    data['comments'] = models.Post.objects.get_comments().count()
    data['users'] = User.objects.filter(is_active=True).count()

    if askbot_settings.GROUPS_ENABLED:
        data['groups'] = models.Group.objects.exclude_personal().count()
    else:
        data['groups'] = 0

    json_string = simplejson.dumps(data)
    return HttpResponse(json_string, mimetype='application/json')

def api_user_info(request, user_id):
    '''
       Returns data about one user
    '''
    user = get_object_or_404(User, pk=user_id)

    data = {}
    data['username'] = user.username
    data['reputation'] = user.reputation
    data['questions'] = models.Post.objects.get_questions(user).count()
    data['answers'] = models.Post.objects.get_answers(user).count()
    #epoch time
    data['date_joined'] =  user.date_joined.strftime('%s')
    data['last_seen'] =  user.last_seen.strftime('%s')

    json_string = simplejson.dumps(data)
    return HttpResponse(json_string, mimetype='application/json')


def api_users_info(request):
    '''
       Returns data of the most active or latest users.
    '''
    allowed_order_by = ('recent', 'oldest', 'reputation', 'username')
    order_by = request.GET.get('order_by', 'reputation')

    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    if order_by not in allowed_order_by:
        raise Http404
    else:
        if order_by == 'reputation':
            users = models.User.objects.exclude(status = 'b').order_by('-reputation')
        elif order_by == 'oldest':
            users = models.User.objects.exclude(status = 'b').order_by('date_joined')
        elif order_by == 'recent':
            users = models.User.objects.exclude(status = 'b').order_by('-date_joined')
        elif order_by == 'username':
            users = models.User.objects.exclude(status = 'b').order_by('username')
        else:
            raise Exception("Order by method not allowed")


        paginator = Paginator(users, 10)

        try:
            user_objects = paginator.page(page)
        except (EmptyPage, InvalidPage):
            user_objects = paginator.page(paginator.num_pages)

        user_list = []
        #serializing to json
        for user in user_objects:
            user_dict = {
                         'id': user.id,
                         'username': user.username,
                         'date_joined': user.date_joined.strftime('%s'),
                         'reputation': user.reputation
                        }
            user_list.append(dict.copy(user_dict))

        response_dict = {
                         'total_pages': paginator.num_pages,
                         'count': paginator.count,
                         'user_list': user_list
                        }
        json_string = simplejson.dumps(response_dict)

        return HttpResponse(json_string, mimetype='application/json')


def api_question_info(request, question_id):
    '''
    Gets a single question
    '''
    post = get_object_or_404(
        models.Post, id=question_id,
        post_type='question', deleted=False
    )
    question_url = '%s%s' % (askbot_settings.APP_URL, post.get_absolute_url())

    response_dict = {
                      'title': post.thread.title,
                      'text': post.text,
                      'username': post.author.username,
                      'user_id': post.author.id,
                      'url': question_url,
                    }

    json_string = simplejson.dumps(response_dict)

    return HttpResponse(json_string, mimetype='application/json')


def api_latest_questions(request):
    """
    List of Questions, Tagged questions, and Unanswered questions.
    matching search query or user selection
    """
    try:
        author_id = int(request.GET.get("author"))
    except (TypeError, ValueError):
        author_id = None

    try:
        page = int(request.GET.get("page"))
    except (TypeError, ValueError):
        page = None

    search_state = SearchState(
                    scope = request.GET.get('scope', 'all'),
                    sort = request.GET.get('sort', 'activity-desc'),
                    query = request.GET.get("query", None),
                    tags = request.GET.get("tags", None),
                    author = author_id,
                    page = page,
                    user_logged_in=request.user.is_authenticated(),
                )

    page_size = int(askbot_settings.DEFAULT_QUESTIONS_PAGE_SIZE)

    qs, meta_data = models.Thread.objects.run_advanced_search(
                        request_user=request.user, search_state=search_state
                    )
    if meta_data['non_existing_tags']:
        search_state = search_state.remove_tags(meta_data['non_existing_tags'])

    #exludes the question from groups
    global_group = models.Group.objects.get_global_group()
    qs = qs.exclude(~Q(groups__id=global_group.id))

    paginator = Paginator(qs, page_size)
    if paginator.num_pages < search_state.page:
        search_state.page = 1
    page = paginator.page(search_state.page)

    question_list = list(page.object_list.values('title', 'view_count',
                                                 'tagnames',
                                                 'id',
                                                 'last_activity_by__username',
                                                 'answer_count'))

    #adds urls
    for i, question in enumerate(question_list):
        question['url'] = '%s%s' % (askbot_settings.APP_URL,
                                    reverse('question',
                                            kwargs={'id': question['id']})
                                   )
        question_list[i] = question

    page.object_list = list(page.object_list) # evaluate the queryset

    models.Thread.objects.precache_view_data_hack(threads=page.object_list)

    ajax_data = {
        'query_data': {
            'tags': search_state.tags,
            'sort_order': search_state.sort,
            'ask_query_string': search_state.ask_query_string(),
        },
        'question_count': paginator.count,
        'query_string': request.META.get('QUERY_STRING', ''),
        'page_size' : page_size,
        'non_existing_tags': meta_data['non_existing_tags'],
        'question_list': question_list
    }

    return HttpResponse(simplejson.dumps(ajax_data),
                        mimetype = 'application/json')
