from inspect import getmembers, ismethod
from django.db import models
from django.db.models.base import ModelBase
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

from rowperm.permissions import BasePermission

class AlreadyRegistered(Exception):
    pass

class NotRegistered(Exception):
    pass

class PermissionSite(object):
    """
    A dictionary that contains permission instances and their labels.
    """
    _registry = {}
    
    def register(self, model_or_iterable, permission_class=None):
        if not permission_class:
            permission_class = BasePermission

        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]

        for model in model_or_iterable:
            if model in self._registry:
                raise AlreadyRegistered(
                    'The model %s is already registered' % model.__name__)
            
            permission_class.model = model
            self._registry[model] = permission_class

    def unregister(self, model_or_iterable):
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model not in self._registry:
                raise NotRegistered('The model %s is not registered' % model.__name__)
            del self._registry[model]

    def get_registered(self):
        return self._registry
    registered = property(get_registered)


site = PermissionSite()
register = site.register
unregister = site.unregister
