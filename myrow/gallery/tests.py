"""
>>> import rowperm.models

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

>>> view_action = Action(codename="view",for_model="gallery")
>>> edit_action = Action(codename="edit",for_model="gallery")
>>> view_action.save()
>>> edit_action.save()
>>> view_action
<Action: Can view for gallery>

>>> from myrow.gallery.models import Gallery
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
[<RowPermission: view-gallery>]

>>> RowPermission.objects.get_perms_for_user(gallery,makkalot,"view")
[<RowPermission: view-gallery>]
>>> RowPermission.objects.get_perms_for_group(gallery,publisher_group,"view")
[]


#lets now create a RowPermission for publisher group
>>> gallery2 = Gallery(name="for_publishers")
>>> gallery2.save()

#edit on that object can be done only via publisher_role
>>> row_perm = RowPermission(code = edit_action,content_object = gallery2,approved = True)
>>> row_perm.save()
>>> row_perm.roles.add(publisher_role)

#when check for makkalot it should return empty
>>> RowPermission.objects.get_perms_for_user(gallery2,makkalot,"edit")
[]

>>> RowPermission.objects.get_perms_for_group(gallery2,publisher_group,"edit")
[<RowPermission: edit-gallery>]

#now we will add the makkalot to publisher group and it should return True
>>> makkalot.groups.add(publisher_group)
>>> RowPermission.objects.get_perms_for_user_group(gallery2,makkalot,"edit")
[<RowPermission: edit-gallery>]

#lets try for a user who is not in that group
>>> fooman = User.objects.create_user("fooman","foo@foo.com","12345")
>>> RowPermission.objects.get_perms_for_user_group(gallery2,fooman,"edit")
[]

>>> res = RowPermission.objects.all()
>>> len(res) == 2
True

>>> RowPermission.objects.delete_objects_permissions(gallery)
>>> RowPermission.objects.all().count()
1

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
[<RowPermission: edit-gallery>]
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
[<RowPermission: edit-gallery>]
>>> c.has_perm('edit',moderator_gallery)
True
>>> c.can('edit',moderator_gallery)
False

"""
