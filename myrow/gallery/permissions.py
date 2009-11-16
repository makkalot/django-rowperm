from rowperm.permissions import *
from myrow.gallery.models import Gallery
import rowperm 

class MyPerm(BasePermission):
    checks = ['can_kiss']

#register the class
rowperm.register(Gallery,MyPerm)
