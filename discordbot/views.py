from django.shortcuts import render
from discordbot.models import Wisdom, Imgur, DiscordUser
from django.http import JsonResponse, HttpResponse
import time

def get_random_entry(model):
    try:
        random_entry = model.objects.filter(pid=0).order_by('?').first()
        model.objects.filter(id=random_entry.id).update(pid=1)
    except:
        model.objects.all().update(pid=0)
        random_entry = model.objects.filter(pid=0).order_by('?').first()
    return random_entry


def mix(request):
    random_wisdom = get_random_entry(Wisdom)
    random_bg = get_random_entry(Imgur)
    return render(request, 'home_page_app/mix.html', {'wisdom_text' : random_wisdom.text, 'bg' : random_bg.url})

def mix_api(request):
    random_wisdom = get_random_entry(Wisdom)
    random_bg = get_random_entry(Imgur)
    return JsonResponse({'wisdom_text' : random_wisdom.text, 'imgur_picture' : random_bg.url})
    
