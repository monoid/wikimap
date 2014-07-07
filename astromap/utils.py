# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.crypto import get_random_string
import datetime
import hashlib
import math
import time
import socket
import struct

import geohash


def deg2hms(deg):
    h = int(math.floor(deg))
    deg = 60.0 * (deg - h)
    m = int(math.floor(deg))
    deg = 60.0 * (deg - m)
    s = int(math.floor(deg))

    return u"%02d°%02d'%02d\"" % (h, m, s)


def inet_aton(ip):
    # http://stackoverflow.com/questions/5619685/conversion-from-ip-string-to-integer-and-backward-in-python
    return struct.unpack('!I', socket.inet_aton(ip))[0]


def gen_rnd_kook(request):
    # $ip = $_SERVER['REMOTE_ADDR'].'_'.$ip_salt;
    ip = request.META['REMOTE_ADDR'] + '_' + settings.IP_SALT
    # $rnd = uniqid($rnd_salt);
    rnd = get_random_string(16)
    # return sha1($ip.'_'.$rnd);
    return hashlib.sha1(ip + '_' + rnd).hexdigest()


OLD_AUTH_COOKIE = 'auth'
AUTH_COOKIE = 'fmauth'

def set_kook(response, kook):
    response.set_cookie(AUTH_COOKIE, kook, expires=(datetime.datetime.now() +
                                                   datetime.timedelta(seconds=20000000)))


def get_kook(request, response):
    if OLD_AUTH_COOKIE in request.COOKIES:
        kook = request.COOKIES[OLD_AUTH_COOKIE]
    elif AUTH_COOKIE in request.COOKIES:
        kook = request.COOKIES[AUTH_COOKIE]
    elif request.user.is_anonymous():
        kook = gen_rnd_kook(request)
    else:
        kook = None
    # Update cookie time.
    if kook:
        set_kook(response, kook)
    return kook


def rebind_points(kook, user):
    u""" Переносим точки от kook user'у.
    """
    pass


def jsonize(dict_rec, kook, user=None):
    val = dict_rec.copy()
    val['drag'] = val['kook'] == kook
    z = val['zoom'] or 13
    val['z'] = val['zoom']
    val['pt'] = geohash.encode(val['point'], 16 + 2*z)
    val['ts'] = int(time.mktime(val['ts'].utctimetuple()))

    del val['kook']
    del val['point']
    del val['ptxt']
    del val['ip']
    del val['zoom']  # var['z'] is used instead

    return val
