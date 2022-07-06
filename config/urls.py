"""
Definition of urls for HomeSite.
"""
from allauth.socialaccount.providers.discord.urls import \
    urlpatterns as discord_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('main.urls')),
    path('games/', include('webgames.urls')),
    path('ladder/', include('poeladder.urls')),
    path('discordbot/', include('discordbot.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('accounts/', include(discord_urls)),
    path('accounts/', include('allauth.socialaccount.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    if settings.MEDIA_URL and settings.MEDIA_ROOT:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
