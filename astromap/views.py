# -*- coding: utf-8 -*-
from django.contrib.gis.feeds import GeoAtom1Feed, Feed
from django.contrib.gis.geos import Point
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import get_language_from_request
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_safe
import json

from astromap import forms, geohash, models, utils
# Create your views here.


@require_safe
@ensure_csrf_cookie
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
        'type': map_type,
    }, RequestContext(request)))
    return response


class AMGeoAtom1Feed(Feed):
    title = u"Карта астрономов-любителей."
    subtitle = u"Последние добавленные и измененённые точки."
    feed_type = GeoAtom1Feed
    link = '/astromap/atom'

    def geometry(self, item):
        return None

    def item_geometry(self, item):
        return item.point

    def items(self):
        return models.Point.objects.all().order_by('-ts')[:10]

    def item_link(self, item):
        return ('http://ivan.ivanych.net/astromap/#' +
                geohash.encode_zoom(item.zoom) +
                geohash.encode(item.point, 16 + 2*item.zoom))

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return u'%s: %s, %s (#%d)' % (
            item.title,
            utils.deg2hms(item.point[0]),
            utils.deg2hms(item.point[1]),
            item.id)

    def item_pubdate(self, item):
        return item.ts



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
        form = forms.InsertForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['txt'].strip()
            lat = form.cleaned_data['lat']
            lon = form.cleaned_data['lon']
            zoom = form.cleaned_data['zoom']
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
        else:
            json.dump({
                'status': 'error',
                'text': u"Invalid query."
            }, response)

    elif cmd == 'updattr':
        form = forms.UpdattrForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['txt'].strip()
            pid = form.cleaned_data['id']
            if title:
                try:
                    pt = models.Point.objects.get(id=pid, kook=kook)
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
        else:
            json.dump({
                'status': 'error',
                'text': u"Invalid query."
            }, response)

    elif cmd == 'updgeom':
        form = forms.UpdgeomForm(request.POST)
        if form.is_valid():
            pid = form.cleaned_data['id']
            lat = form.cleaned_data['lat']
            lon = form.cleaned_data['lon']
            zoom = form.cleaned_data['zoom']

            try:
                pt = models.Point.objects.get(id=pid, kook=kook)
                pt.zoom = zoom
                pt.point = Point(lat, lon)
                pt.save()
            except models.Point.DoesNotExist:
                pass  # Если точка не найдена или чужая, делаем вид, что всё ОК
            json.dump({
                'status': 'OK'
            }, response)
        else:
            json.dump({
                'status': 'error',
                'text': u"Invalid query."
            }, response)

    elif cmd == 'del':
        form = forms.DelForm(request.POST)
        if form.is_valid():
            pid = form.cleaned_data['id']

            try:
                pt = models.Point.objects.get(id=pid, kook=kook)
                pt.delete()
            except models.Point.DoesNotExist:
                pass  # Если точка не найдена или чужая, делаем вид, что всё ОК
            json.dump({
                'status': 'OK'
            }, response)
        else:
            json.dump({
                'status': 'error',
                'text': u"Invalid query."
            }, response)

    else:
        json.dump({
            'status': 'error',
            'text': u"Unknown command."
        }, response)

    return response


# def auth_handler(request):
#     return ''
