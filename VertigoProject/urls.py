"""
Definition of urls for HomeSite.
"""

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework import routers

from main.viewsets import CharacterViewSet

router = routers.DefaultRouter()
router.register(r'characters', CharacterViewSet)
admin.autodiscover()

urlpatterns = [
    #url(r'^books', include('books.urls')),
    url(r'^', include('main.urls')),
    url(r'^games/', include('unitygames.urls')),
    url(r'^ladder/', include('poeladder.urls')),
    # Rest
    url(r'^api/v1/', include('discordbot.urls')),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # Admin
    url('admin/', admin.site.urls),
    ] 

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
