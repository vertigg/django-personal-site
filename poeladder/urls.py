from django.conf.urls import include, url
from .views import ladder_view, league_ladder_view

urlpatterns = [
    url(r'^$', ladder_view),
    url(r'^(?P<league>[\w\-]+)/$', league_ladder_view, name='ladder_url'),
]