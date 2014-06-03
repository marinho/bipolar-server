from django.conf.urls import patterns, include, url
from api import v1_api

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'', include("bipolar_server.toggle.urls")),
)
