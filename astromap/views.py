# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.utils.translation import get_language_from_request
from django.views.decorators.http import require_POST, require_safe
from django.views.decorators.vary import vary_on_headers
import json

from astromap import models, utils
# Create your views here.

@require_safe
def index(request):
    u""" Index page.
    """
    kook = utils.get_kook(request)
    pts = [utils.jsonize(pt, kook) for pt in models.Point.objects.values()]
    lang = get_language_from_request(request)
    map_type = request.GET.get('type', 'normal')
    # Renders template
    return render(request, 'index.html', {
        'PTS_JSON': json.dumps(pts),
        'LANG': lang,
        # TODO use django.utils.translation
        'lang_file_js': 'lang/lang_'+lang+'.js',
        'type': map_type,
    })


@require_safe
def atom_feed(request):
    u""" An ATOM feed. """
    return HttpResponse(u'atom')


@require_safe
def kml_feed(request):
    u""" A KML feed for Google Earth etc. """
    return HttpResponse(u'kml')


def login(request, token=None):
    u""" Login page and login handler, both old and social. """
    return HttpResponse(u'login')


@require_POST
def ajax_handler(request):
    u""" AJAX handling: point creation, modification, etc. """
    return HttpResponse(u'ajax')


# def auth_handler(request):
#     return ''
