from django.conf.urls import include, url
from .views import warframe_webhook

urlpatterns = [
    url(r'warframe-webhook', warframe_webhook, name='warframe_webhook'),
]
