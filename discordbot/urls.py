from django.urls import path
from discordbot.views import WarframeWebhookView, corona_report

app_name = 'discordbot'

urlpatterns = [
    path('warframe-webhook', WarframeWebhookView.as_view(), name='warframe_webhook'),
    path('corona-report', corona_report, name='corona_report'),
]
