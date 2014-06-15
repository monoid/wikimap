import time
import geohash

def get_kook(request):
    return ''

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