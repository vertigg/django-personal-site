from .models import PoeLeague, PoeInfo
from datetime import datetime
from django.utils import timezone

def posix_to_datetime(posix):
    return datetime.fromtimestamp(int(posix)).strftime('%Y-%m-%d %H:%M:%S')

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
