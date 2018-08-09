from datetime import datetime
from django.utils import timezone
from .forms import SearchForm
from .models import PoeInfo, PoeLeague


def header_urls(request):
    leagues_with_players = PoeLeague.objects.filter(poecharacter__isnull=False).distinct()
    temp_leagues = leagues_with_players.filter(end_date__gt=timezone.localtime())
    old_leagues = leagues_with_players.exclude(id__in=temp_leagues)
    return {'old_leagues' : old_leagues, 'temp_leagues' : temp_leagues}

def last_ladder_update(request):
    try:
        db_time = PoeInfo.objects.get(key='last_update').timestamp
        update_time = timezone.localtime(db_time)
    except Exception as e:
        update_time = e
    return {'last_update' : update_time}


def poe_search_form(request):
    return {'poe_search_form' : SearchForm()}
