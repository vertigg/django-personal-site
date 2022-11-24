from django.utils import timezone
from django.utils.functional import SimpleLazyObject

from poe.forms import SearchForm
from poe.models import PoeInfo, League


def poe_info(request):
    def get_poe_context():
        leagues_with_players = League.objects.filter(
            character__isnull=False).distinct()
        temp_leagues = leagues_with_players.filter(
            end_date__gt=timezone.localtime())
        old_leagues = leagues_with_players.exclude(id__in=temp_leagues)
        try:
            db_time = PoeInfo.objects.get(key='last_update').timestamp
            update_time = timezone.localtime(db_time)
        except (AttributeError, PoeInfo.DoesNotExist):
            update_time = None
        return {
            'old_leagues': old_leagues,
            'temp_leagues': temp_leagues,
            'last_update': update_time,
            'search_form': SearchForm
        }
    return {'poe_context': SimpleLazyObject(get_poe_context)}
