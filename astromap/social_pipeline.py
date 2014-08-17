from django.contrib import messages
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
            npoints = Point.objects.filter(kook=kook).update(owner=user, kook=None)
            messages.success("%d more points have been assigned to your user account." % npoints)


def login_successful(strategy, user, request, **kwargs):
    messages.success(request, u"Login successful.")
