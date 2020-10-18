from django.urls import path

from discordbot.views import (CoronaChartView, MixPoll, MixPollGallery,
                              WarframeWebhookView)

app_name = 'discordbot'

urlpatterns = [
    path('warframe-webhook', WarframeWebhookView.as_view(), name='warframe_webhook'),
    path('corona-report', CoronaChartView.as_view(), name='corona_report'),
    path('mix/detail', MixPoll.as_view(), name='mix_detail'),
    path('mix/all', MixPollGallery.as_view(), name='mix_gallery')
]
