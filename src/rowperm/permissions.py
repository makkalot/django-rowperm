from django.db.models.base import Model, ModelBase
from django.template.defaultfilters import slugify

from rowperm.models import RowPermission
import inspect 

class PermissionMetaclass(type):
    """
    Used to generate the default set of permission checks "add", "change" and
    "delete".
    """
    def __new__(cls, name, bases, attrs):
        new_class = super(
            PermissionMetaclass, cls).__new__(cls, name, bases, attrs)
        if new_class.checks is None:
            new_class.checks = []
        # force check names to be lower case
        new_class.checks = [check.lower() for check in new_class.checks]
        return new_class

class BasePermission(object):
    """
    Base Permission class to be used to define app permissions.
    """
    __metaclass__ = PermissionMetaclass
    _model = None

    checks = ()
    generic_checks = ['add', 'browse', 'change', 'delete']

    def __init__(self, user=None, group=None, *args, **kwargs):
        self.user = user
        self.group = group
        super(BasePermission, self).__init__(*args, **kwargs)

    def _get_model(self):
        return self._model

    def _set_model(self,model):
        self._model = model

    model = property(_get_model,_set_model)
    
    def has_user_perms(self, perm, obj, approved=True):
        if self.user:
            if self.user.is_superuser:
                return True
            if not self.user.is_active:
                return False
            # check if a Permission object exists for the given params
            return RowPermission.objects.get_perms_for_user(obj,self.user,perm,approved).filter(object_id=obj.id)
        return False

    def has_group_perms(self, perm, obj, approved=True):
        """
        Check if group has the permission for the given object
        """
        if self.group:
            perms = RowPermission.objects.get_perms_for_group(obj,self.group,perm,approved)
            return perms.filter(object_id=obj.id)
        return False

    def has_perm(self, perm, obj,approved=True,check_groups=False):
        """
        Check if user has the permission for the given object
        """
        if self.user:
            if self.has_user_perms(perm, obj, approved):
                return True
        #that one is for situations where you supply the user and want to
        #search its group to see if any of groups it belongs to is able todo that
            if check_groups:#should we look at groups user belongs to
                if RowPermission.objects.get_perms_for_user_group(obj,self.user,perm,approved):
                    return True
        if self.group:
            if self.has_group_perms(perm, obj, approved):
                return True
        
        return False
    
    
    def can(self, check, obj, *args, **kwargs):
        perms = False
        
        if not isinstance(obj, (ModelBase, Model)):
            return False
        
        # first check Django's permission system
        if self.user:
            perm = '%s.%s' % (obj._meta.app_label, check.lower())
            perms = perms or self.user.has_perm(perm)
            if perms:
                return perms
           
            # then check authority's per object permissions
            if not isinstance(obj, ModelBase) and isinstance(obj, self._model):
                perms = perms or self.has_perm(check.lower(), obj,check_groups=True)
                
                # we should check if user added a method for custom checking
                if perms and hasattr(self,check.lower()) and inspect.ismethod(getattr(self,check.lower())):
                    if not getattr(self,check.lower())(*args,**kwargs):
                        return False
                    else:
                        return True
        return perms

