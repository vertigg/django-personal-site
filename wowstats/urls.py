from wowstats import views
from django.conf.urls import url

app_name = "wowstats"

urlpatterns = [
    url(r'^$', views.MainView.as_view(), name='main'),
    url(r'^callback/$', views._callback, name="callback"),
    url(r'^track/$', views.track, name='track'),
    url(r'^charts-data/$', views.get_month_stats, name='charts_data'),
    url(r'^(?P<realm>.+)/(?P<name>.+)$',
        views.CharacterView.as_view(), name='detail'),
]
