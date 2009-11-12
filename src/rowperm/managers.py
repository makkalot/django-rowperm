from django.db import models
from django.contrib.contenttypes.models import ContentType

#some parts taken from django-authority

class RoleManager(models.Manager):

    def get_roles_for_object(self,obj):
        """
        Get roles for that object
        """
        from rowperm.models import RoleItem
        role_items = RoleItem.objects.for_object(obj)
        return [i.role for i in role_items]

    def get_role_names_for_object(self,obj):
        """
        Get only names
        """
        return [i.role_name for i in self.get_roles_for_object(obj)]

class RoleItemManager(models.Manager):
    """
    Manager for RoleItem
    """
    def get_content_type(self, obj):
        return ContentType.objects.get_for_model(obj)

    def get_for_model(self, obj):
        return self.filter(content_type=self.get_content_type(obj))

    def for_object(self, obj):
        """
        When you need to pull roles for a certain object you can use that method.
        """
        return self.get_for_model(obj).select_related('content_type','role').filter(object_id=obj.id)


class RowPermissionManager(models.Manager):
    """
    Manager for RowPermissions
    """

    def get_content_type(self, obj):
        return ContentType.objects.get_for_model(obj)

    def get_for_model(self, obj):
        return self.filter(content_type=self.get_content_type(obj))

    def for_object(self, obj, approved=True):
        return self.get_for_model(obj).select_related(
                'creator','content_type','code'
        ).filter(object_id=obj.id,approved=approved)
    
    def get_perms_for_user(self,obj,user,perm,approved=True):
        """
        Gets the perms for certain user
        """
        from rowperm.models import Role
        role_names = Role.objects.get_role_names_for_object(user)
        return self.for_object(obj).filter(roles__role_name__in=role_names,code__codename=perm,approved=approved)

    def get_perms_for_group(self,obj,group,perm,approved=True):
        """
        The same as above only for api thing
        """
        return self.get_perms_for_user(obj,group,perm,approved)

    def get_perms_for_user_group(self,obj,user,perm,approved=True):
        """
        That is a little different from the one that is above
        it gets the groups that user belongs to and then checks
        each of them to see if that group has the perm wee need
        or to be more clear to see if group has the role for the
        action
        """
        for group in user.groups.all():
            result = self.get_perms_for_group(obj,group,perm,approved)
            if result:
                return result
        return []

    def delete_objects_permissions(self, obj):
        """
        Delete permissions related to an object instance
        """
        perms = self.for_object(obj)
        perms.delete()
