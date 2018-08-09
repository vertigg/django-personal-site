from django.conf.urls import url
import poeladder.views as views

app_name = 'poeladder'

urlpatterns = [
    url(r'^$', views.ladder, name='ladder_main'),
    url(r'^search/$', views.search, name="ladder_search"),
    url(r'^(?P<slug>.+)/$', views.league_ladder, name='ladder_url'),
]