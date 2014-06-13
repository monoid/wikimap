from django.conf.urls import patterns, include, url
from astromap import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^atom$', views.atom_feed),
    url(r'^kml$', views.kml_feed),
    url(r'^login$', views.login),
    url(r'^login/', views.login),
    url(r'^ajax$', views.ajax_handler),
    # url(r'^auth$', views.auth_handler),
)
