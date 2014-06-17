# -*- coding: utf-8 -*-
from django.contrib.gis.geos import Point
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import get_language_from_request
from django.views.decorators.http import require_POST, require_safe
import json

from astromap import models, utils
# Create your views here.

@require_safe
def index(request):
    u""" Index page.
    """
    response = HttpResponse(content_type='text/html; charset=utf-8')
    kook = utils.get_kook(request, response)
    pts = [utils.jsonize(pt, kook) for pt in models.Point.objects.values()]
    lang = get_language_from_request(request)
    map_type = request.GET.get('type', 'normal')
    # Renders template

    response.write(render_to_string('index.html', {
        'PTS_JSON': json.dumps(pts),
        'LANG': lang,
        # TODO use django.utils.translation
        'lang_file_js': 'lang/lang_'+lang+'.js',
        'type': map_type,
    }, RequestContext(request)))
    return response


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
    # Мы заранее создаём response, чтобы get_kook установил в нём новую куку.
    # Затем мы в этот response пишем с помощью json.dump.
    response = HttpResponse(content_type='application/json')
    kook = utils.get_kook(request, response)
    cmd = request.POST.get('cmd', None)
    ip = utils.inet_aton(request.META['REMOTE_ADDR'])

    if cmd == 'insert':
        # TODO: insert form
        title = request.POST['txt'].strip()
        lat = float(request.POST['lat'])
        lon = float(request.POST['lon'])
        zoom = int(request.POST['zoom'])
        if title:
            pt = models.Point.objects.create(
                title=title,
                mapid=2,
                zoom=zoom,
                point=Point(lat, lon),
                kook=kook,
                ip=ip,
                ptxt='',  # Was used for debug of PHP version...
            )
            json.dump({
                'status': 'OK',
                'id': pt.id
            }, response)
        else:
            json.dump({
                'status': 'errror',
                'text': u"Title cannot be empty."
            }, response)

    elif cmd == 'updattr':
        # TODO updattr form
        title = request.POST['txt'].strip()
        id = int(request.POST['id'])
        if title:
            try:
                pt = models.Point.objects.get(id=id, kook=kook)
                pt.title = title
                pt.save()
            except models.Point.DoesNotExist:
                pass  # Если точка не найдена, делаем вид, что всё ОК
            json.dump({
                'status': 'OK'
            }, response)
        else:
            json.dump({
                'status': 'errror',
                'text': u"Title cannot be empty."
            }, response)

    elif cmd == 'updgeom':
        # TODO updgeom form
        id = int(request.POST['id'])
        lat = float(request.POST['lat'])
        lon = float(request.POST['lon'])
        zoom = int(request.POST['zoom'])

        try:
            pt = models.Point.objects.get(id=id, kook=kook)
            pt.zoom = zoom
            pt.point = Point(lat, lon)
            pt.save()
        except models.Point.DoesNotExist:
            pass  # Если точка не найдена или чужая, делаем вид, что всё ОК
        json.dump({
            'status': 'OK'
        }, response)

    elif cmd == 'del':
        # TODO del form
        id = int(request.POST['id'])

        try:
            pt = models.Point.objects.get(id=id, kook=kook)
            pt.delete()
        except models.Point.DoesNotExist:
            pass  # Если точка не найдена или чужая, делаем вид, что всё ОК
        json.dump({
            'status': 'OK'
        }, response)
    else:
        json.dump({
            'status': 'error',
            'text': u"Unknown command."
        }, response)

    return response


# def auth_handler(request):
#     return ''
