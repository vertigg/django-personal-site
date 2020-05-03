import json

import pandas as pd
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView

from discordbot.models import CoronaReport, WFAlert


class CoronaChartView(TemplateView):
    template_name = 'coronareport.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        df = pd.DataFrame.from_dict(
            CoronaReport.objects
            .filter(timestamp__hour=0)
            .values('timestamp', 'deaths', 'recovered', 'confirmed')
            .order_by('timestamp')
            .values()
        )
        context.update({
            "categories": list(df.timestamp.dt.strftime('%Y-%m-%d')),
            'recovered': list(df.recovered),
            'deaths': list(df.deaths),
            'confirmed': list(df.confirmed)
        })
        return context


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
