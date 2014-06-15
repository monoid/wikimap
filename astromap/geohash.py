import math

# __all__ = ['encode']

_tr = "0123456789bcdefghjkmnpqrstuvwxyz"

## This is an opposite of _tr table: it maps #bABCDE to #bA0B0C0D0E.
_dr = [0, 1, 4, 5, 16, 17, 20, 21, 64, 65, 68, 69, 80,
       81, 84, 85, 256, 257, 260, 261, 272, 273, 276, 277,
       320, 321, 324, 325, 336, 337, 340, 341]


def _sparse(val):
    '''
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
    '''
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
    l = int(math.ceil(bits/10))

    for i in xrange(l):
        lat *= 0x20
        lon *= 0x20

        hlt = min(0x1F, int(math.floor(lat)))
        hln = min(0x1F, int(math.floor(lon)))

        lat -= hlt
        lon -= hln

        b2 = _sparse(hlt) | (_sparse(hln) << 1)

        hi = b2 >> 5
        lo = b2 & 0x1F
        r += _tr[hi] + _tr[lo]

    return r[:int(math.ceil(bits/5))]