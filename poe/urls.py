from django.urls import include, path

from poe import views
from poe.routers import LadderRouter
from poe.viewsets import CharacterViewSet, LeagueViewSet, StashHistoryAPIView

app_name = 'poe'

router = LadderRouter()
router.register(r'characters', CharacterViewSet)
router.register(r'leagues', LeagueViewSet)

urlpatterns = [
    path('', views.MainLadderView.as_view(), name='ladder_main'),
    path('api/', include(router.urls)),
    path('api/stash', StashHistoryAPIView.as_view()),
    path('search/', views.LadderSearchView.as_view(), name="ladder_search"),
    path('ladder/<slug>/', views.LadderView.as_view(), name='ladder_url'),
    path('stash/', views.StashHistoryView.as_view(), name='stash'),
    path('chat/', views.TestView.as_view(), name='chat-monitor'),
]
