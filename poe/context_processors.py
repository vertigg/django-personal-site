from django.utils import timezone
from django.utils.functional import SimpleLazyObject

from poe.forms import SearchForm
from poe.models import League


def poe_info(request):
    def get_poe_context():
        leagues = League.objects.filter(character__isnull=False).distinct()
        temp_leagues = leagues.filter(end_date__gt=timezone.localtime())
        old_leagues = leagues.exclude(id__in=temp_leagues)
        return {
            'old_leagues': old_leagues,
            'temp_leagues': temp_leagues,
            'search_form': SearchForm,
            'tools_links': {
                ('Path of Building Community', 'https://pathofbuilding.community/'),
                ('Official Trade Website', 'https://www.pathofexile.com/trade'),
                ('poe.ninja', 'https://poe.ninja/challenge/builds'),
                ('Betrayal Cheat Sheet', 'https://hashbr.github.io/betrayal-cs'),
                ('Vorici Chromatic Calculator', 'https://siveran.github.io/calc.html'),
                ('Aura Calculator', 'https://poe.mikelat.com/')
            }
        }
    return {'poe_context': SimpleLazyObject(get_poe_context)}
