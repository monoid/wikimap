import astromap.utils
from astromap.models import Point


__author__ = 'ib'


# TODO: @partial pipeline that asks if points should be associated
# with the user.
def register_points(strategy, user, request, **kwargs):
    if user and not user.is_authenticated():
        kook = astromap.utils.get_kook(request, None)
        if kook:
            # Assign points to the user
            Point.objects.filter(kook=kook).update(owner=user, kook=None)