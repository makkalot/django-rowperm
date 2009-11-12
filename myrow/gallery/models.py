from django.db import models
from django.utils.translation import get_language, ugettext_lazy as _


class Gallery(models.Model):
    
    name = models.CharField(max_length=30)
    
class Picture(models.Model):
    gallery = models.ForeignKey(Gallery,editable=False,blank=True,null=True)
    description = models.CharField(max_length=60)

    class Meta:
        permissions = (
                ("can_see", "Can View Pictures (Globally)",),
                )
