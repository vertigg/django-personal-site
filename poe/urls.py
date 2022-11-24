from django.urls import include, path

from poe import views
from poe.routers import LadderRouter
from poe.viewsets import CharacterViewSet, LeagueViewSet

# Temp
from django.contrib.auth.views import TemplateView


app_name = 'poe'

router = LadderRouter()
router.register(r'characters', CharacterViewSet)
router.register(r'leagues', LeagueViewSet)

urlpatterns = [
    path('', views.MainLadderView.as_view(), name='ladder_main'),
    path('api/', include(router.urls)),
    path('search/', views.LadderSearchView.as_view(), name="ladder_search"),
    path('ladder/<slug>/', views.LadderView.as_view(), name='ladder_url'),
    path('stash/', TemplateView.as_view(template_name='stash.html'), name='stash'),
]
