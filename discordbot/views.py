import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from discordbot.models import WFAlert


@method_decorator(csrf_exempt, name='dispatch')
class WarframeWebhookView(View):
    def get_alert_content(self, data):
        if 'api_key' in data and data['api_key'] == settings.WARFRAME_KEY:
            return data.get('content')
        raise Http404

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        content = self.get_alert_content(data)
        WFAlert.objects.create(content=content)
        return JsonResponse({'status': 'success'}, status=201)
