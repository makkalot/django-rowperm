"""

>>> def generate_code_name(code,model):return "%s.%s.%s"%(code.lower(),model._meta.module_name,model._meta.app_label)

>>> import rowperm.models
>>> from myrow.gallery.models import *

>>> moderator_role = rowperm.models.Role(role_name="moderator",display_name="Moderator Role")
>>> moderator_role.save()
>>> rowperm.models.Role(role_name="moderator",display_name="Moderator Role")
<Role: Moderator Role>

>>> publisher_role = rowperm.models.Role(role_name="publisher",display_name="Publisher Role")
>>> publisher_role.save()
>>> publisher_role
<Role: Publisher Role>

>>> from django.contrib.auth.models import User
>>> makkalot = User.objects.create_user("makix","makix@maka.com","1234")

>>> from rowperm.models import *

>>> ri = RoleItem(role=moderator_role,content_object=makkalot)
>>> ri.save()
>>> ri
<RoleItem: Moderator Role-user>

>>> from django.contrib.auth.models import Group
>>> publisher_group = Group(name="pubgr")
>>> publisher_group.save()
>>> rg = RoleItem(role=publisher_role,content_object=publisher_group)
>>> rg.save()
>>> rg
<RoleItem: Publisher Role-group>

>>> view_action = Action(codename=generate_code_name("view",Gallery))
>>> edit_action = Action(codename=generate_code_name("edit",Gallery))
>>> view_action.save()
>>> edit_action.save()
>>> view_action
<Action: gallery| gallery | Can view>
>>> gallery = Gallery(name="important")
>>> gallery.save()
>>> row_perm = RowPermission(code = view_action,content_object = gallery,approved = True)
>>> row_perm.save()
>>> row_perm.roles.add(moderator_role)

#now lets test the managers

>>> user_roles = Role.objects.get_roles_for_object(makkalot)
>>> user_roles
[<Role: Moderator Role>]

>>> user_names = Role.objects.get_role_names_for_object(makkalot)
>>> user_names
[u'moderator']


>>> RoleItem.objects.for_object(makkalot)
[<RoleItem: Moderator Role-user>]
>>> RoleItem.objects.for_object(publisher_group)
[<RoleItem: Publisher Role-group>]

>>> RowPermission.objects.for_object(gallery)
[<RowPermission: gallery| gallery | Can view-gallery>]

>>> RowPermission.objects.get_perms_for_user(gallery,makkalot,generate_code_name("view",Gallery))
[<RowPermission: gallery| gallery | Can view-gallery>]

>>> RowPermission.objects.get_perms_for_group(gallery,publisher_group,generate_code_name("view",Gallery))
[]


#lets now create a RowPermission for publisher group
>>> gallery2 = Gallery(name="for_publishers")
>>> gallery2.save()

#edit on that object can be done only via publisher_role
>>> row_perm = RowPermission(code = edit_action,content_object = gallery2,approved = True)
>>> row_perm.save()
>>> row_perm.roles.add(publisher_role)

#when check for makkalot it should return empty
>>> RowPermission.objects.get_perms_for_user(gallery2,makkalot,generate_code_name("edit",Gallery))
[]

>>> RowPermission.objects.get_perms_for_group(gallery2,publisher_group,generate_code_name("edit",Gallery))
[<RowPermission: gallery| gallery | Can edit-gallery>]

#now we will add the makkalot to publisher group and it should return True
>>> makkalot.groups.add(publisher_group)
>>> RowPermission.objects.get_perms_for_user_group(gallery2,makkalot,generate_code_name("edit",Gallery))
[<RowPermission: gallery| gallery | Can edit-gallery>]

#lets try for a user who is not in that group
>>> fooman = User.objects.create_user("fooman","foo@foo.com","12345")
>>> RowPermission.objects.get_perms_for_user_group(gallery2,fooman,generate_code_name("edit",Gallery))
[]

>>> res = RowPermission.objects.all()
>>> len(res) == 2
True

>>> RowPermission.objects.delete_objects_permissions(gallery)
>>> RowPermission.objects.all().count()
1

#---------------------------------------------------------------------------------------------
#now we should test the permissions.py stuff
>>> from rowperm.permissions import *
>>> class GalleryPerm(BasePermission):
...     checks = ['moderate']

>>> c=GalleryPerm(makkalot)
>>> moderator_gallery = Gallery(name="moderator_things")
>>> moderator_gallery.save()
>>> row_perm2 = RowPermission(code = edit_action,content_object = moderator_gallery,approved = True)
>>> row_perm2.save()
>>> row_perm2.roles.add(moderator_role)
>>> c.model = Gallery #that one will be set automatically when registering
>>> c.has_user_perms('edit',moderator_gallery)
[<RowPermission: gallery| gallery | Can edit-gallery>]
>>> c.has_perm('edit',moderator_gallery)
True
>>> c.can('edit',moderator_gallery)
True


#lets now do that with a user who has no perms
>>> from django.contrib.auth.models import User
>>> noperm_user = User.objects.create_user("linux","linux@linux.com","1234")
>>> c=GalleryPerm(noperm_user)
>>> c.model = Gallery #that one will be set automatically when registering
>>> c.has_user_perms('edit',moderator_gallery)
[]
>>> c.has_perm('edit',moderator_gallery)
False
>>> c.can('edit',moderator_gallery)
False
>>> noperm_user.groups.add(publisher_group)
>>> c.has_perm('edit',moderator_gallery,check_groups=True)
False
>>> c.can('edit',moderator_gallery)
False
>>> row_perm2.roles.add(publisher_role)
>>> c.has_perm('edit',moderator_gallery,check_groups=True)
True
>>> c.can('edit',moderator_gallery)
True

#lets do the same thing with Group first do it with a group
#that doesnt have the rights and then add rights so we ca see how 
#it accepts the stuuf easy huh ...
>>> row_perm2.roles.remove(publisher_role)
>>> c=GalleryPerm(group=publisher_group)
>>> c.model = Gallery #that one will be set automatically when registering
>>> c.has_group_perms('edit',moderator_gallery)
[]
>>> c.has_perm('edit',moderator_gallery)
False
>>> c.can('edit',moderator_gallery)
False

#now lets add the perm to that object so that group can do that action there
>>> row_perm2.roles.add(publisher_role)
>>> c.has_group_perms('edit',moderator_gallery)
[<RowPermission: gallery| gallery | Can edit-gallery>]
>>> c.has_perm('edit',moderator_gallery)
True
>>> c.can('edit',moderator_gallery)
False

#--------------------------------------------------------------------------------

>>> class CustomGalleryPerm(BasePermission):
...     checks = ['custom_check_yes','custom_check_no','not_custom']
...
...     def custom_check_yes(self,*args,**kwargs):
...         return True
...
...     def custom_check_no(self,*args,**kwargs):
...         return False


#creating the actions these will be created in initialization
>>> custom_check_yes_action = Action(codename=generate_code_name("custom_check_yes",Gallery))
>>> custom_check_no_action = Action(codename=generate_code_name("custom_check_no",Gallery))
>>> not_custom_action = Action(codename=generate_code_name("not_custom",Gallery))
>>> custom_check_yes_action.save()
>>> custom_check_no_action.save()
>>> not_custom_action.save()

>>> custom_perm = CustomGalleryPerm(makkalot)
>>> custom_perm.custom_check_yes()
True

>>> custom_perm.model = Gallery #that one will be set automatically when registering
>>> custom_gallery = Gallery(name="custom_things")
>>> custom_gallery.save()

>>> row_perm3 = RowPermission(code = custom_check_yes_action,content_object = custom_gallery,approved = True)
>>> row_perm3.save()
>>> row_perm3.roles.add(moderator_role)

>>> row_perm4 = RowPermission(code = custom_check_no_action,content_object = custom_gallery,approved = True)
>>> row_perm4.save()
>>> row_perm4.roles.add(moderator_role)

>>> row_perm5 = RowPermission(code = not_custom_action,content_object = custom_gallery,approved = True)
>>> row_perm5.save()
>>> row_perm5.roles.add(moderator_role)



>>> custom_perm.has_user_perms('custom_check_yes',custom_gallery)
[<RowPermission: gallery| gallery | Can custom_check_yes-gallery>]
>>> custom_perm.has_perm('custom_check_yes',custom_gallery)
True
>>> custom_perm.can('custom_check_yes',custom_gallery)
True

>>> custom_perm.has_user_perms('custom_check_no',custom_gallery)
[<RowPermission: gallery| gallery | Can custom_check_no-gallery>]
>>> custom_perm.has_perm('custom_check_no',custom_gallery)
True
>>> custom_perm.can('custom_check_no',custom_gallery)
False

>>> custom_perm.has_user_perms('not_custom',custom_gallery)
[<RowPermission: gallery| gallery | Can not_custom-gallery>]
>>> custom_perm.has_perm('not_custom',custom_gallery)
True
>>> custom_perm.can('not_custom',custom_gallery)
True

#----------------------------------------------------------------------------------------------------
"""
