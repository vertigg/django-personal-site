import json

import pandas as pd
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import Http404, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from discordbot.models import CoronaReport, WFAlert


def corona_report(request):
    qs = (CoronaReport.objects
          .filter(timestamp__hour=0)
          .values('timestamp', 'deaths', 'recovered', 'confirmed')
          .order_by('timestamp')
          )
    df = pd.DataFrame.from_dict(qs)
    categories = list(df.timestamp.dt.strftime('%Y-%m-%d'))
    deaths = list(df.deaths)
    recovered = list(df.recovered)
    confirmed = list(df.confirmed)

    context = {
        "categories": categories,
        'recovered': recovered,
        'deaths': deaths,
        'confirmed': confirmed
    }
    return render(request, 'coronareport.html', context=context)


@method_decorator(csrf_exempt, name='dispatch')
class WarframeWebhookView(View):
    def get_alert_content(self, data):
        if 'api_key' in data and data['api_key'] == settings.WARFRAME_KEY:
            return data.get('content')
        return Http404

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        content = self.get_alert_content(data)
        WFAlert.objects.create(content=content)
        return JsonResponse({'status': 'success'}, status=201)
