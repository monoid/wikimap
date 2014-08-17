from django.conf.urls import patterns, url, static
from django.views.decorators.cache import cache_page
from django_dont_vary_on.decorators import dont_vary_on
from astromap import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^atom$', cache_page(5*60)(
        dont_vary_on('Cookie', 'Accept-Language')(
            views.AMGeoAtom1Feed())),
        name='atom'),
    url(r'^kml$', views.kml_feed, name='kml'),
    url(r'^login$', views.login, name='login'),
    url(r'^login/+(.*)$', views.login),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^ajax$', views.ajax_handler),
    # url(r'^auth$', views.auth_handler),
)
