from django.urls import path

from discordbot.views import WarframeWebhookView

app_name = 'discordbot'

urlpatterns = [
    path('warframe-webhook', WarframeWebhookView.as_view(), name='warframe_webhook'),
]
