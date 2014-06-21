import math

# __all__ = ['encode', 'decode', 'encode_zoom']
from django.contrib.gis.geos.point import Point

_tr = "0123456789bcdefghjkmnpqrstuvwxyz"

## This is an opposite of _tr table: it maps #bABCDE to #bA0B0C0D0E.
_dr = [0, 1, 4, 5, 16, 17, 20, 21, 64, 65, 68, 69, 80,
       81, 84, 85, 256, 257, 260, 261, 272, 273, 276, 277,
       320, 321, 324, 325, 336, 337, 340, 341]

_dm = (0, 1, 0, 1, 2, 3, 2, 3, 0, 1, 0, 1, 2, 3, 2, 3,
       4, 5, 4, 5, 6, 7, 6, 7, 4, 5, 4, 5, 6, 7, 6, 7)


def _cmb(s, p):
    return (_tr.find(s[p]) << 5) | _tr.find(s[p+1])


def _unp(v):
    return _dm[v & 0x1F] | ((_dm[v >> 6] & 0xF) << 3)


def decode(string):
    le = len(string)
    ln = 0.0
    lt = 0.0

    if le & 1:
        w = _tr.find(string[le-1]) << 5
    else:
        w = _cmb(string, le-2)
    lt = _unp(w) / 32.0
    ln = _unp(w >> 1) / 32.0

    for i in xrange((le - 2) & ~1, -1, -2):
        w = _cmb(string, i)
        lt = (_unp(w) + lt) / 32.0
        ln = (_unp(w >> 1) + ln) / 32.0

    ln = 360.0*(ln-0.5)
    lt = 180.0*(lt-0.5)
    return Point(lt, ln)


def _sparse(val):
    """
    :param val: number
    :return: val with 0 bits inserted between each original bit. 0b111 => 0b10101.

    >>> _sparse(1)
    1
    >>> _sparse(2)
    4
    >>> _sparse(3)
    5
    >>> _sparse(4)
    16
    """
    acc = 0
    off = 0

    while val > 0:
        low = val & 0x1F
        acc |= _dr[low] << off
        val >>= 5
        off += 10

    return acc


def encode(pt, bits):
    lat, lon = pt
    lat = lat/180.0+0.5
    lon = lon/360.0+0.5

    r = ''
    l = int(math.ceil(bits/10.0))

    for i in xrange(l):
        lat *= 0x20
        lon *= 0x20

        hlt = min(0x1F, int(lat))
        hln = min(0x1F, int(lon))

        lat -= hlt
        lon -= hln

        b2 = _sparse(hlt) | (_sparse(hln) << 1)

        hi = b2 >> 5
        lo = b2 & 0x1F
        r += _tr[hi] + _tr[lo]

    return r[:int(math.ceil(bits/5.0))]


def encode_zoom(zoom):
    if zoom < 0:
        zoom = 0
    elif zoom > 31:
        zoom = 31
    return _tr[zoom]


def is_valid(string):
    # TODO real implementation
    return True