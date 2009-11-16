# -*- coding: utf-8 -*-
#some parts taken from django-authority

from datetime import datetime
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from rowperm.managers import *

class Role(models.Model):
    """
    Roles of the users and groups
    """
    role_name = models.CharField(verbose_name=_('Role Name'), max_length=100,help_text=_("Name of the role that will be assigned "),unique=True)
    display_name = models.CharField(verbose_name=_('Displayed Role Name'), max_length=100)
    
    objects = RoleManager()

    def save(self, *args, **kwargs):
        self.role_name = slugify(self.role_name)
        super(Role, self).save(*args, **kwargs)
   
    def __unicode__(self):
        return self.display_name

    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')

class RoleItem(models.Model):
    """
    RoleType is model that will be attached to Groups and Users models
    a ContentType thing
    """
    role = models.ForeignKey(Role,related_name='role_items')

    content_type = models.ForeignKey(ContentType,related_name="attached_roles")
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    objects = RoleItemManager()

    class Meta:
        unique_together = ("role","object_id", "content_type")
        verbose_name = _('roletype')
        verbose_name_plural = _('roletypes')

    def __unicode__(self):
        return "%s-%s"%(self.role,str(self.content_type))
   


class Action(models.Model):
    """
    Here we will define the actions that can be made on 
    objects,ex. moderate_comment and etc
    """
    #the format is like action.model.appname
    codename = models.CharField(verbose_name=_('codename'), max_length=100,unique=True)
    
    def __unicode__(self):
        codes = self.codename.split(".")
        return "%s| %s | Can %s"%(codes[2],codes[1],codes[0])


class RowPermission(models.Model):
    """
    A granular permission model, per-object permission in other words.
    This kind of permission is associated with an object
    of any content type.
    """
    code = models.ForeignKey(Action,help_text=_("Designates the code that will be applied to that row"))
    roles = models.ManyToManyField(Role,related_name="object_roles",help_text=_("Which roles can do that ?"))

    content_type = models.ForeignKey(ContentType, related_name="row_permissions")
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    creator = models.ForeignKey(User, null=True, blank=True, related_name='created_permissions')
    approved = models.BooleanField(_('approved'), default=True, help_text=_("Designates whether the permission has been approved and treated as active. Unselect this instead of deleting permissions."))
    date_requested = models.DateTimeField(_('date requested'), default=datetime.now)
    date_approved = models.DateTimeField(_('date approved'), blank=True, null=True)

    objects = RowPermissionManager()

    def __unicode__(self):
        return "%s-%s"%(self.code,self.content_type)

    class Meta:
        unique_together = ("code","object_id", "content_type")
        verbose_name = _('rowpermission')
        verbose_name_plural = _('rowpermissions')
        permissions = (
            ('change_row_permissions', 'Can change row permissions'),
            ('delete_row_permissions', 'Can delete row permissions'),
            ('approve_row_requests', 'Can approve row permission requests'),
        )

    def save(self, *args, **kwargs):
        # Make sure the approval date is always set
        if self.approved and not self.date_approved:
            self.date_approved = datetime.now()
        super(RowPermission, self).save(*args, **kwargs)

    def approve(self, creator):
        """
        Approve granular permission request setting a RowPermission entry as
        approved=True for a specific action from an user on an object instance.
        """
        self.approved = True
        self.creator = creator
        self.save()


