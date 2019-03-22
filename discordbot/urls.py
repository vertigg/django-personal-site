from django.urls import path
from discordbot.views import warframe_webhook

urlpatterns = [
    path('warframe-webhook', warframe_webhook, name='warframe_webhook'),
]
