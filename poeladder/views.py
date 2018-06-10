import random

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from .filters import PoeCharacterFilter
from .forms import SearchForm
from .models import PoeCharacter, PoeInfo, PoeLeague


def ladder(request):
    return render(request, 'poeladder/ladder.html', {
        'title' : None,
        'ladder_main' : True
        })


def league_ladder(request, league):
    """View for league-specific ladder """
    requested_league = league.replace('-', ' ').strip()
    league_object = get_object_or_404(PoeLeague, name=requested_league)
    title = '{} League'.format(requested_league)

    query_set = PoeCharacter.objects.all().filter(league_id=league_object.id).order_by('-level', '-experience')
    league_characters = PoeCharacterFilter(request.GET, query_set)
    current_profile = request.user.discorduser.poe_profile if hasattr(request.user, 'discorduser') else None

    return render(request, 'poeladder/ladder.html', {
        'title': title,
        'league_object': league_object, 
        'requested_league': requested_league,
        'league_characters': league_characters,
        'current_profile' : current_profile
        })


def search(request):
    """View for cross-league character search by name"""
    response = {'search' : True, 'title' : 'Search results'}
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            name = form.cleaned_data['name']
            response['search_query'] = request.GET['name'] if name else 'All characters' 
            response['search_results'] = PoeCharacter.objects.filter(name__icontains=name).order_by('name')
    return render(request, 'poeladder/ladder.html', response)
