from django.urls import include, path

import poeladder.views as views
from poeladder.viewsets import CharacterViewSet
from poeladder.routers import LadderRouter

app_name = 'poeladder'

router = LadderRouter()
router.register(r'characters', CharacterViewSet)

urlpatterns = [
    path('', views.ladder, name='ladder_main'),
    path('api/', include(router.urls)),
    path('search/', views.search, name="ladder_search"),
    path('<slug>/', views.league_ladder, name='ladder_url'),
]
