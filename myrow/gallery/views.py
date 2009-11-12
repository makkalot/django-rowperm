from django.shortcuts import render_to_response,get_object_or_404
from django.template import RequestContext
from django.http import Http404

from myrow.gallery.models import *

def get_pictures(request):
    """
    The items to be got
    """
    pictures = Picture.objects.all()

    return render_to_response(
            "base.html",
            {
                'pictures':pictures,
                },
            context_instance=RequestContext(request)
            )


