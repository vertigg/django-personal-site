from django.shortcuts import render
from django.http import HttpResponse, Http404
from .models import PoeCharacter, PoeInfo, PoeLeague
from django.shortcuts import get_object_or_404
from .filters import PoeCharacterFilter

def media_url(request):
    from django.conf import settings
    return {'media_url': settings.MEDIA_URL}

def ladder_view(request):
    leagues = [x.name for x in PoeLeague.objects.all()]
    print(leagues)
    return render(request, 'poeladder/ladder.html', {'title':None})

def league_ladder_view(request, league):

    requested_league = league.replace('-', ' ').strip()
    league_object = get_object_or_404(PoeLeague, name=requested_league)
    title = '{} League'.format(requested_league)

    query_set = PoeCharacter.objects.all().filter(league_id=league_object.id).order_by('-level')
    league_characters = PoeCharacterFilter(request.GET, query_set)

    return render(request, 'poeladder/ladder.html', {
        'title':title,
        'league_object': league_object, 
        'requested_league':requested_league,
        'league_characters': league_characters,
        })
