import random

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from .filters import PoeCharacterFilter
from .forms import SearchForm
from .models import PoeCharacter, PoeLeague


def ladder(request):
    return render(request, 'poeladder/ladder.html', {
        'ladder_main' : True
        })


def league_ladder(request, slug):
    """View for league-specific ladder """
    active_league = get_object_or_404(PoeLeague, slug=slug)
    title = '{} League'.format(active_league.name)

    query_set = PoeCharacter.objects.all().filter(league_id=active_league.id).order_by('-level', '-experience')
    league_characters = PoeCharacterFilter(request.GET, query_set)
    current_profile = request.user.discorduser.poe_profile if hasattr(request.user, 'discorduser') else None

    return render(request, 'poeladder/ladder.html', {
        'active_league': active_league,
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
