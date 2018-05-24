from django.conf.urls import include, url
import poeladder.views as views

urlpatterns = [
    url(r'^$', views.ladder, name='ladder_main'),
    url(r'^search/$', views.search, name="ladder_search"),
    url(r'^(?P<league>[\w\-\S]+)/$', views.league_ladder, name='ladder_url'),
]