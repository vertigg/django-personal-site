import json
import re

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from discordbot.models import WFAlert

re_invasion = r'\((.*?)\)'


@csrf_exempt
def warframe_webhook(request):
    try:
        if request.method == "POST":
            json_data = json.loads(request.body.decode('utf-8'))
            if 'api_key' in json_data and json_data['api_key'] == settings.WARFRAME_KEY:
                content = json_data['content']
                new_alert = WFAlert(content=content)
                if 'Invasion' in content:
                    filtered_data = re.findall(re_invasion, content)
                    filtered_data.pop(0)
                    new_alert.keywords = ','.join(filtered_data)
                elif 'Sortie' in content:
                    new_alert.keywords = 'Sortie'
                else:
                    raw_data = content.split('-')
                    if len(raw_data) is 4:
                        if 'kavat' in raw_data[3].lower():
                            new_alert.keywords = 'kavat'
                        else:
                            new_alert.keywords = raw_data[3].strip()
                new_alert.save()
                return JsonResponse({'status': 201})
        return redirect('main:home')
    except Exception as e:
        return HttpResponse(e)
