from django.conf.urls import include, url
from .views import mix_api

urlpatterns = [
    url(r'mix/', mix_api, name='mix_api'),
]