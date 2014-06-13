from django.conf.urls import patterns, include, url

import astromap.urls

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ivanivanych.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^astromap/', include(astromap.urls)),
    url(r'^admin/', include(admin.site.urls)),
)
