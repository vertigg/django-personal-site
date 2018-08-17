from django.conf.urls import url, include

import poeladder.views as views
from poeladder.viewsets import CharacterViewSet
from poeladder.routers import LadderRouter

app_name = 'poeladder'

router = LadderRouter()
router.register(r'characters', CharacterViewSet)

urlpatterns = [
    url(r'^$', views.ladder, name='ladder_main'),
    url(r'^api/', include(router.urls)),
    url(r'^search/$', views.search, name="ladder_search"),
    url(r'^(?P<slug>.+)/$', views.league_ladder, name='ladder_url'),
]
