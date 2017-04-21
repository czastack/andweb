from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import RedirectView
from .handler import BaseHandler, subpatterns


urlpatterns = (
    url(r'^admin/', admin.site.urls),
    url('^', include(subpatterns)),
    url(r'(.*)', BaseHandler.dispatch),
)

