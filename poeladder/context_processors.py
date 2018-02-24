from .models import PoeLeague, PoeInfo
from datetime import datetime
from django.utils import timezone
from .forms import SearchForm


def header_urls(request):
    leagues_names = [x.name for x in PoeLeague.objects.filter(poecharacter__isnull=False).distinct().order_by('-start_date')]
    return {'header_urls': leagues_names}


def last_ladder_update(request):
    try:
        db_time = PoeInfo.objects.get(key='last_update').timestamp
        update_time = timezone.localtime(db_time)
    except Exception as e:
        update_time = e
    return {'last_update': update_time}


def poe_search_form(request):
    form = SearchForm()
    return {'poe_search_form': form}