from django.conf.urls import patterns, url, static
from astromap import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^atom$', views.AMGeoAtom1Feed()),
    url(r'^kml$', views.kml_feed),
    url(r'^login$', views.login),
    url(r'^login/', views.login),
    url(r'^ajax$', views.ajax_handler),
    # url(r'^auth$', views.auth_handler),
)
