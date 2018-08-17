from django.conf.urls import url
from unitygames import views

urlpatterns = [
    url(r'^asteroids/$', views.asteroids, name='asteroids'),
]
