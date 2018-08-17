from wowstats import views
from django.conf.urls import url

app_name = "wowstats"

urlpatterns = [
    url(r'^bnet/$', views.callback, name="callback"),
    url(r'^$', views.main, name='main'),
    # url(r'^$', views.CharactersView.as_view(), name='main'),
]
