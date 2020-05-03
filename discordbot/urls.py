from django.urls import path

from discordbot.views import CoronaChartView, WarframeWebhookView

app_name = 'discordbot'

urlpatterns = [
    path('warframe-webhook', WarframeWebhookView.as_view(), name='warframe_webhook'),
    path('corona-report', CoronaChartView.as_view(), name='corona_report'),
]
