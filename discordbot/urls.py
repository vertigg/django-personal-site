from django.urls import path

from discordbot.views import MixPoll, MixPollGallery, WarframeWebhookView

app_name = 'discordbot'

urlpatterns = [
    path('warframe-webhook', WarframeWebhookView.as_view(), name='warframe_webhook'),
    path('mix/detail', MixPoll.as_view(), name='mix_detail'),
    path('mix/all', MixPollGallery.as_view(), name='mix_gallery')
]
