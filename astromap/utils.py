from django.conf import settings
from django.utils.crypto import get_random_string
import datetime
import hashlib
import time
import socket
import struct

import geohash

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


def get_kook(request, response):
    if OLD_AUTH_COOKIE in request.COOKIES:
        kook = request.COOKIES[OLD_AUTH_COOKIE]
    elif AUTH_COOKIE in request.COOKIES:
        kook = request.COOKIES[AUTH_COOKIE]
    else:
        kook = gen_rnd_kook(request)
    # Update cookie time.
    response.set_cookie(AUTH_COOKIE, kook, expires=(datetime.datetime.now() +
                                                   datetime.timedelta(seconds=20000000)))
    return kook


def jsonize(dict_rec, kook):
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