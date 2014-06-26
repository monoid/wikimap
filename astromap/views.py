# -*- coding: utf-8 -*-
from django.contrib.gis.feeds import GeoAtom1Feed, Feed
from django.contrib.gis.geos import Point
from django.contrib.gis.geos.polygon import Polygon
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import get_language_from_request
from django.views.decorators.cache import cache_page, never_cache, cache_control
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_safe
from django.views.i18n import javascript_catalog
from django_dont_vary_on.decorators import dont_vary_on
import json
import hashlib
import uuid

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
    feed_type = GeoAtom1Feed
    link = '/astromap/atom'

    # Used by dont_vary_on
    __name__ = 'astromap.views.AMGeoAtom1Feed'

    WINDOW_MODES = frozenset(['window', 'map'])
    LATEST_MODES = frozenset(['latest', 'simple'])
    FULL_MODES = frozenset(['all', 'full'])

    VALID_MODES = WINDOW_MODES | LATEST_MODES | FULL_MODES

    def get_object(self, request, *args, **kwargs):
        args = request.GET
        mode = args.get('mode', 'simple')

        if mode not in self.VALID_MODES:
            raise Http404(u"Incorrect mode.")

        if mode in self.WINDOW_MODES:
            if 'lb' in args and 'rt' in args and \
                    geohash.is_valid(args['lb']) and \
                    geohash.is_valid(args['rt']):
                return {
                    'mode': mode,
                    'lb': args['lb'],
                    'rt': args['rt']
                }
            else:
                return {'mode': 'latest'}

        return {'mode': mode}

    def subtitle(self, params):
        mode = params['mode']
        if mode in self.FULL_MODES:
            return u"Все точки."
        else:
            return u"Последние добавленные и изменённые точки."

    def item_geometry(self, item):
        return item['point']

    def items(self, params):
        objs = models.Point.objects.all().values(
            'id', 'ts', 'title', 'point', 'zoom')
        mode = params['mode']

        if mode in self.FULL_MODES:
            return objs
        elif mode in self.WINDOW_MODES:
            lbx, lby = geohash.decode(params['lb'])
            rtx, rty = geohash.decode(params['rt'])
            poly = Polygon.from_bbox((min(lbx, rtx), min(lby, rty),
                                      max(lbx, rtx), max(lby, rty)))
            objs = objs.filter(point__contained=poly)

        objs = objs[:10]

        return objs

    def item_link(self, item):
        zoom = item['zoom']
        return ('http://ivan.ivanych.net/astromap/#' +
                geohash.encode_zoom(zoom) +
                geohash.encode(item['point'], 16 + 2*zoom))

    def item_title(self, item):
        return item['title']

    def item_description(self, item):
        return u'%s: %s, %s (#%d)' % (
            item['title'],
            utils.deg2hms(item['point'][0]),
            utils.deg2hms(item['point'][1]),
            item['id'])

    def item_pubdate(self, item):
        return item['ts']

    def item_guid(self, item):
        hash_id = hashlib.sha1(str(item['id'])).digest()[:16]
        return uuid.UUID(bytes=hash_id).urn


@cache_page(86400, key_prefix='js18n-00')
@dont_vary_on('Cookie', 'Accept-Language')
@require_safe
def kml_feed(request):
    u""" A KML feed for Google Earth etc. """
    return render(request, 'feed.kml', {
        'records': models.Point.objects.all(),
        'icon_uri': request.build_absolute_uri(
            staticfiles_storage.url('icons32/circle-star.png')),
    }, content_type='application/vnd.google-earth.kml+xml; charset=utf-8')


#@never_cache  # Brocken, see https://code.djangoproject.com/ticket/13008
@cache_control(max_age=0, no_cache=True, no_store=True)
def login(request, token=None):
    u""" Login page and login handler, both old and social. """
    if token:
        response = HttpResponse(content_type='text/html; coding=utf-8')
        utils.set_kook(response, token)
        response.write(render_to_string('login-isset.html', {'token': token},
                                        RequestContext(request)))
        return response
    else:
        response = HttpResponse(content_type='text/html; coding=utf-8')
        kook = utils.get_kook(request, response)
        response.write(render_to_string('login-show.html', {
            'login_url': request.build_absolute_uri(
                "%s/%s" % (reverse('login'), kook,)),
        }, RequestContext(request)))
        return response


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


@cache_page(86400, key_prefix='js18n-00')
@dont_vary_on('Cookie')
def cached_javascript_catalog(request, domain='djangojs', packages=None):
    return javascript_catalog(request, domain, packages)

# def auth_handler(request):
#     return ''
