import json

import pandas as pd
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models.query_utils import Q
from django.http import JsonResponse
from django.shortcuts import Http404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView, View

from discordbot.forms import MixPollEntryForm
from discordbot.models import MixImage, MixPollEntry, WFAlert


@method_decorator(csrf_exempt, name='dispatch')
class WarframeWebhookView(View):
    def get_alert_content(self, data):
        if 'api_key' in data and data['api_key'] == settings.WARFRAME_KEY:
            return data.get('content')
        return Http404

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        content = self.get_alert_content(data)
        WFAlert.objects.create(content=content)
        return JsonResponse({'status': 'success'}, status=201)


class MixPollGallery(LoginRequiredMixin, ListView):
    model = MixImage

    def get_queryset(self):
        return super().get_queryset().filter(deleted=False).order_by('id')


class MixPoll(LoginRequiredMixin, ListView):
    model = MixImage
    paginate_by = 1
    template_name = 'discordbot/miximage_detail.html'

    def get_queryset(self):
        return (super().get_queryset().filter(deleted=False)
                .order_by('id').select_related('author'))

    def get_user_like(self, image):
        obj = MixPollEntry.objects.filter(
            user=self.request.user, image=image).first()
        return obj.liked if obj else None

    def get_total_votes(self, image):
        return MixPollEntry.objects.filter(image=image).aggregate(
            likes=Count('liked', filter=Q(liked=True)),
            dislikes=Count('liked', filter=Q(liked=False))
        )

    def get_first_paginated_image(self, context):
        page = context.get('page_obj')
        return page.object_list[0] if page and page.object_list.exists() else None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image = self.get_first_paginated_image(context)
        context['user_like'] = self.get_user_like(image)
        initial_data = {'user': self.request.user, 'image': image}
        context['like_form'] = MixPollEntryForm(initial={**initial_data, **{'liked': True}})
        context['dislike_form'] = MixPollEntryForm(initial={**initial_data, **{'liked': False}})
        context['total_votes'] = self.get_total_votes(image)
        context['image'] = image
        return context

    def post(self, request):
        form = MixPollEntryForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.build_absolute_uri())
