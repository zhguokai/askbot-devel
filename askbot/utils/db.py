"""database model utilities"""
from django import forms
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404

def assert_user_can_access_object_property(user, obj, params):
    """validation function, raises PermissionDenied if 
    assertion fails"""
    model_name = params['model_name']
    attribute_name = params['attribute_name']
    if model_name == 'Group' and attribute_name == 'description__text':
        if user.is_authenticated() and user.is_administrator_or_moderator():
            return
    elif model_name == 'auth.User' and attribute_name == 'about':
        if user.is_authenticated():
            if user == obj or user.is_administrator_or_moderator():
                return
    raise PermissionDenied()
    

def get_db_object_or_404(params):
    """a utility function that returns an object
    in return to the model_name and object_id

    only specific models are accessible
    """
    from askbot import models
    try:
        model_name = params['model_name']
        model = models.get_model(model_name)
        obj_id = forms.IntegerField().clean(params['object_id'])
        return get_object_or_404(model, id=obj_id)
    except Exception:
        #need catch-all b/c of the nature of the function
        raise Http404


def get_attribute_by_lookup_path(obj, path):
    """for example, obj can be askbot.models.Group and path 'description__text'"""
    path_bits = path.split('__')
    attr_name = path_bits.pop()
    if len(path_bits):
        obj = get_attribute_by_lookup_path(obj, '__'.join(path_bits))
    return getattr(obj, attr_name, '')
