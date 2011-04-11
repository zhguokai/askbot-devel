from categories.models import Category
from mptt.templatetags.mptt_tags import cache_tree_children

from django.http import Http404, HttpResponse
from django.utils import simplejson

from askbot.conf import settings as askbot_settings
from askbot.skins.loaders import render_into_skin


def cats(request):
    """
    View that renders a simple page showing the categories tree widget.
    It uses JSON to send tree data in the context to the client.
    """
    if askbot_settings.ENABLE_CATEGORIES:
        roots = cache_tree_children(Category.tree.all())
        root_node = roots[0]
        data =  simplejson.dumps(_recurse_tree(root_node))
        return render_into_skin(
                'categories.html',
                {'cats_tree': data},
                request
        )
    else:
        raise Http404

def _recurse_tree(node):
    """
    Traverses recursively a node tree and builds a Python structure easily
    serializable as JSON.
    """
    output = {'name': node.name}
    children = []
    if not node.is_leaf_node():
        for child in node.get_children():
            children.append(_recurse_tree(child))
    output['children'] = children
    return output

# Old code follows

def _build_ul(node):
    """Helper recursive function for render_ul()."""
    output = []
    output.append(u'<li>%s' % node.name)
    if not node.is_leaf_node():
        output.append(u'<ul>')
        for child in node.get_children():
            output.append(_build_ul(child))
        output.append(u'</ul>')
    output.append(u'</li>')
    return u'\n'.join(output)

def render_ul(node):
    """
    Renders a django-category Category (actually, a django-mptt node)
    hierarchy as a tree of nested HTML ul/li tags.
    """
    return u'<ul>\n%s\n</ul>' % _build_ul(node)

def cats_dump(request):
    """
    View that renders a simple page showing the categories tree.
    """
    if askbot_settings.ENABLE_CATEGORIES:
        roots = cache_tree_children(Category.tree.all())
        root_node = roots[0]
        return HttpResponse(u'<html><body>%s</body></html>' % render_ul(root_node))
    else:
        raise Http404
