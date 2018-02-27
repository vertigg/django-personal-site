"""
Definition of urls for HomeSite.
"""

from django.conf.urls import include, url

from django.conf import settings
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from HomePageApp.views import home_view
from UnityAsteroidsClone.views import asteroids_view
from VertigoProject.views import show_datetime, hours_ahead
admin.autodiscover()

urlpatterns = [

    url(r'^$', home_view, name='home'),
    url(r'^asteroids/$', asteroids_view, name='asteroids'),
    url(r'^date/', show_datetime),
    url(r'^time/plus/(\d{1,2})/$', hours_ahead),
    url(r'^ladder/', include('poeladder.urls')),
    url(r'^api/v1/', include('discordbot.urls')),
    #url(r'^books', include('books.urls')),

    #Uncomment the next line to enable the admin:
    url('admin/', admin.site.urls),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
