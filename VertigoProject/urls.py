"""
Definition of urls for HomeSite.
"""

from django.conf.urls import include, url

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from django.contrib import admin
from VertigoProject.views import home_view, signup
from UnityAsteroidsClone.views import asteroids_view

admin.autodiscover()

urlpatterns = [

    # url('^', include('django.contrib.auth.urls')),
    url(r'^$', home_view, name='home'),
    url(r'^asteroids/$', asteroids_view, name='asteroids'),
    url(r'^ladder/', include('poeladder.urls')),
    url(r'^api/v1/', include('discordbot.urls')),
    #url(r'^books', include('books.urls')),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'home'}, name='logout'),
    #url(r'^signup/$', signup, name='signup'),
    
    #Uncomment the next line to enable the admin:
    url('admin/', admin.site.urls),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
