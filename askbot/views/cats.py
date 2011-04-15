from categories.models import Category
from mptt.templatetags.mptt_tags import cache_tree_children

#from django.db import IntegrityError
from django.core import exceptions
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.utils.translation import ugettext as _

from askbot.conf import settings as askbot_settings
from askbot.models import Tag
from askbot.skins.loaders import render_into_skin


def cats(request):
    """
    View that renders a simple page showing the categories tree widget.
    It uses JSON to send tree data in the context to the client.
    """
    if askbot_settings.ENABLE_CATEGORIES:
        return render_into_skin(
            'categories.html',
            {'cats_tree':simplejson.dumps(generate_tree())},
            request
        )
    else:
        raise Http404

def generate_tree():
    """
    Traverses a node tree and builds a structure easily serializable as JSON.
    """
    roots = cache_tree_children(Category.tree.all())
    if roots:
        # Assume we have one tree for now, this could change if we decide
        # against storing the root node in the DB
        return _recurse_tree(roots[0])
    return {}

def _recurse_tree(node):
    """
    Helper recursive function for generate_tree().
    Traverses recursively the node tree.
    """
    output = {'name': node.name, 'id': (node.tree_id, node.lft)}
    children = []
    if not node.is_leaf_node():
        for child in node.get_children():
            children.append(_recurse_tree(child))
    output['children'] = children
    return output

def add_category(request):
    """
    Adds a category. Meant to be called by the site administrator using ajax
    and POST HTTP method.
    The expected json request is an object with the following keys:
      'name':   Name of the new category to be created.
      'parent': ID of the parent category for the category to be created.
    The response is also a json object with keys:
      'success': boolean
      'message': text description in case of failure (not always present)

    Category IDs are two-elements [tree_id, left id] JS arrays (Python tuples)
    """
    if not askbot_settings.ENABLE_CATEGORIES:
        raise Http404
    response_data = dict()
    try:
        if request.is_ajax():
            if request.method == 'POST':
                if request.user.is_authenticated():
                    if request.user.is_administrator():
                        post_data = simplejson.loads(request.raw_post_data)
                        parent = post_data.get('parent')
                        new_name = post_data.get('name')
                        if not new_name:
                            raise exceptions.ValidationError(
                                _("Missing or invalid new category name parameter")
                                )
                        if parent:
                            try:
                                parent = Category.objects.get(
                                        tree_id=parent[0],
                                        lft=parent[1]
                                    )
                            except Category.DoesNotExist:
                                raise exceptions.ValidationError(
                                    _("Requested parent category doesn't exist")
                                    )
                        cat, created = Category.objects.get_or_create(name=new_name, parent=parent)
                        if not created:
                            raise exceptions.ValidationError(
                                _('There is already a category with that name')
                                )
                        response_data['success'] = True
                        data = simplejson.dumps(response_data)
                        return HttpResponse(data, mimetype="application/json")
                    else:
                        raise exceptions.PermissionDenied(
                            _('Sorry, but you cannot access this view')
                        )
                else:
                    raise exceptions.PermissionDenied(
                        _('Sorry, but anonymous users cannot access this view')
                    )
            else:
                raise exceptions.PermissionDenied('must use POST request')
        else:
            #todo: show error page but no-one is likely to get here
            return HttpResponseRedirect(reverse('index'))
    except Exception, e:
        message = unicode(e)
        if message == '':
            message = _('Oops, apologies - there was some error')
        response_data['message'] = message
        response_data['success'] = False
        data = simplejson.dumps(response_data)
        return HttpResponse(data, mimetype="application/json")

def rename_category(request):
    """
    Change the name of a category. Meant to be called by the site administrator
    using ajax and POST HTTP method.
    The expected json request is an object with the following keys:
      'id':   ID of the category to be renamed.
      'name': New name of the category.
    The response is also a json object with keys:
      'success': boolean
      'message': text description in case of failure (not always present)

    Category IDs are two-elements [tree_id, left id] JS arrays (Python tuples)
    """
    if not askbot_settings.ENABLE_CATEGORIES:
        raise Http404
    response_data = dict()
    try:
        if request.is_ajax():
            if request.method == 'POST':
                if request.user.is_authenticated():
                    if request.user.is_administrator():
                        post_data = simplejson.loads(request.raw_post_data)
                        new_name = post_data.get('name')
                        cat_id = post_data.get('id')
                        if not new_name or not cat_id:
                            raise exceptions.ValidationError(
                                _("Missing or invalid required parameter")
                                )
                        try:
                            node = Category.objects.get(
                                    tree_id=cat_id[0],
                                    lft=cat_id[1]
                                )
                        except Category.DoesNotExist:
                            raise exceptions.ValidationError(
                                _("Requested category doesn't exist")
                                )
                        if new_name != node.name:
                            # TODO: return a third 'noop' status?
                            try:
                                node = Category.objects.get(name=new_name)
                            except Category.DoesNotExist:
                                pass
                            else:
                                raise exceptions.ValidationError(
                                    _('There is already a category with that name')
                                    )
                            node.name=new_name
                            # Let any exception that happens during save bubble up,
                            # for now
                            node.save()
                        response_data['success'] = True
                        data = simplejson.dumps(response_data)
                        return HttpResponse(data, mimetype="application/json")
                    else:
                        raise exceptions.PermissionDenied(
                            _('Sorry, but you cannot access this view')
                        )
                else:
                    raise exceptions.PermissionDenied(
                        _('Sorry, but anonymous users cannot access this view')
                    )
            else:
                raise exceptions.PermissionDenied('must use POST request')
        else:
            #todo: show error page but no-one is likely to get here
            return HttpResponseRedirect(reverse('index'))
    except Exception, e:
        message = unicode(e)
        if message == '':
            message = _('Oops, apologies - there was some error')
        response_data['message'] = message
        response_data['success'] = False
        data = simplejson.dumps(response_data)
        return HttpResponse(data, mimetype="application/json")

def add_tag_to_category(request):
    """
    Adds a tag to a category. Meant to be called by the site administrator using ajax
    and POST HTTP method.
    Both the tag and the category must exist and their IDs are provided to
    the view.
    The expected json request is an object with the following keys:
      'tag_id': ID of the tag.
      'cat_id': ID of the category.
    The response is also a json object with keys:
      'success': boolean
      'message': text description in case of failure (not always present)

    Category IDs are two-elements [tree_id, left id] JS arrays (Python tuples)
    """
    if not askbot_settings.ENABLE_CATEGORIES:
        raise Http404
    response_data = dict()
    try:
        if request.is_ajax():
            if request.method == 'POST':
                if request.user.is_authenticated():
                    if request.user.is_administrator():
                        post_data = simplejson.loads(request.raw_post_data)
                        tag_id = post_data.get('tag_id')
                        cat_id = post_data.get('cat_id')
                        if not tag_id or cat_id is None:
                            raise exceptions.ValidationError(
                                _("Missing required parameter")
                                )
                        try:
                            cat = Category.objects.get(
                                    tree_id=cat_id[0],
                                    lft=cat_id[1]
                                )
                        except Category.DoesNotExist:
                            raise exceptions.ValidationError(
                                _("Requested category doesn't exist")
                                )
                        try:
                            tag = Tag.objects.get(id=tag_id)
                        except Tag.DoesNotExist:
                            raise exceptions.ValidationError(
                                _("Requested tag doesn't exist")
                                )
                        # Let any exception that happens during save bubble up
                        tag.categories.add(cat)
                        response_data['success'] = True
                        data = simplejson.dumps(response_data)
                        return HttpResponse(data, mimetype="application/json")
                    else:
                        raise exceptions.PermissionDenied(
                            _('Sorry, but you cannot access this view')
                        )
                else:
                    raise exceptions.PermissionDenied(
                        _('Sorry, but anonymous users cannot access this view')
                    )
            else:
                raise exceptions.PermissionDenied('must use POST request')
        else:
            #todo: show error page but no-one is likely to get here
            return HttpResponseRedirect(reverse('index'))
    except Exception, e:
        message = unicode(e)
        if message == '':
            message = _('Oops, apologies - there was some error')
        response_data['message'] = message
        response_data['success'] = False
        data = simplejson.dumps(response_data)
        return HttpResponse(data, mimetype="application/json")

def get_tag_categories(request):
    """
    Get the categories a tag belongs to. Meant to be called using ajax
    and POST HTTP method. Available to everyone including anonymous users.
    The expected json request is an object with the following key:
      'tag_id': ID of the tag. (required)
    The response is also a json object with keys:
      'success': boolean
      'cats':    a list of two-elements lists containing category ID
         (integer) name (string) for each category
      'message': text description in case of failure (not always present)
    """
    if not askbot_settings.ENABLE_CATEGORIES:
        raise Http404
    response_data = dict()
    try:
        if request.is_ajax():
            if request.method == 'POST':
                post_data = simplejson.loads(request.raw_post_data)
                tag_id = post_data.get('tag_id')
                if not tag_id:
                    raise exceptions.ValidationError(
                        _("Missing tag_id parameter")
                        )
                try:
                    tag = Tag.objects.get(id=tag_id)
                except Tag.DoesNotExist:
                    raise exceptions.ValidationError(
                        _("Requested tag doesn't exist")
                        )
                response_data['cats'] = list(tag.categories.values('id', 'name'))
                response_data['success'] = True
                data = simplejson.dumps(response_data)
                return HttpResponse(data, mimetype="application/json")
            else:
                raise exceptions.PermissionDenied('must use POST request')
        else:
            #todo: show error page but no-one is likely to get here
            return HttpResponseRedirect(reverse('index'))
    except Exception, e:
        message = unicode(e)
        if message == '':
            message = _('Oops, apologies - there was some error')
        response_data['message'] = message
        response_data['success'] = False
        data = simplejson.dumps(response_data)
        return HttpResponse(data, mimetype="application/json")

def remove_tag_from_category(request):
    """
    Remove a tag from a category it tag belongs to. Meant to be called using ajax
    and POST HTTP method. Available to admin and moderators users.
    The expected json request is an object with the following keys:
      'tag_id': ID of the tag.
      'cat_id': ID of the category.
    The response is also a json object with keys:
      'success': boolean
      'cats':    a list of two-elements lists containing category ID
         (integer) name (string) for each category
      'message': text description in case of failure (not always present)

    Category IDs are two-elements [tree_id, left id] JS arrays (Python tuples)
    """
    if not askbot_settings.ENABLE_CATEGORIES:
        raise Http404
    response_data = dict()
    try:
        if request.is_ajax():
            if request.method == 'POST':
                if request.user.is_authenticated():
                    if request.user.is_administrator() or request.user.is_moderator():
                        post_data = simplejson.loads(request.raw_post_data)
                        tag_id = post_data.get('tag_id')
                        cat_id = post_data.get('cat_id')
                        if not tag_id or cat_id is None:
                            raise exceptions.ValidationError(
                                _("Missing required parameter")
                                )
                        try:
                            cat = Category.objects.get(
                                    tree_id=cat_id[0],
                                    lft=cat_id[1]
                                )
                        except Category.DoesNotExist:
                            raise exceptions.ValidationError(
                                _("Requested category doesn't exist")
                                )
                        try:
                            tag = Tag.objects.get(id=tag_id)
                        except Tag.DoesNotExist:
                            raise exceptions.ValidationError(
                                _("Requested tag doesn't exist")
                                )
                        # TODO: return a third 'noop' status?
                        if cat.tags.filter(id=tag.id).count():
                            # Let any exception that happens during save bubble up
                            cat.tags.remove(tag)
                        response_data['success'] = True
                        data = simplejson.dumps(response_data)
                        return HttpResponse(data, mimetype="application/json")
                    else:
                        raise exceptions.PermissionDenied(
                            _('Sorry, but you cannot access this view')
                        )
                else:
                    raise exceptions.PermissionDenied(
                        _('Sorry, but anonymous users cannot access this view')
                    )
            else:
                raise exceptions.PermissionDenied('must use POST request')
        else:
            #todo: show error page but no-one is likely to get here
            return HttpResponseRedirect(reverse('index'))
    except Exception, e:
        message = unicode(e)
        if message == '':
            message = _('Oops, apologies - there was some error')
        response_data['message'] = message
        response_data['success'] = False
        data = simplejson.dumps(response_data)
        return HttpResponse(data, mimetype="application/json")
