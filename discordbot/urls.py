from django.urls import path
from discordbot.views import WarframeWebhookView

urlpatterns = [
    path('warframe-webhook', WarframeWebhookView.as_view(), name='warframe_webhook'),
]
