from django.conf.urls import patterns, include, url

import astromap.urls

from django.contrib import admin
admin.autodiscover()

js_info_dict = {
    'packages': ('astromap',),
}

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ivanivanych.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^astromap/', include(astromap.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url('^social/', include('social.apps.django_app.urls', namespace='social')),
    (r'^jsi18n/$', 'astromap.views.cached_javascript_catalog', js_info_dict),
)
