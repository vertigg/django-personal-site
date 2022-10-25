from django.urls import include, path

from poeladder import views
from poeladder.routers import LadderRouter
from poeladder.viewsets import CharacterViewSet, LeagueViewSet

app_name = 'poeladder'

router = LadderRouter()
router.register(r'characters', CharacterViewSet)
router.register(r'leagues', LeagueViewSet)

urlpatterns = [
    path('', views.MainLadderView.as_view(), name='ladder_main'),
    path('api/', include(router.urls)),
    path('search/', views.LadderSearchView.as_view(), name="ladder_search"),
    path('<slug>/', views.LadderView.as_view(), name='ladder_url')
]
