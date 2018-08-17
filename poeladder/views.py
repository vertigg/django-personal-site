import random

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from poeladder.filters import PoeCharacterFilter
from poeladder.forms import SearchForm
from poeladder.models import PoeCharacter, PoeLeague


def ladder(request):
    return render(request, 'poeladder/ladder.html', {
        'ladder_main': True
    })


def league_ladder(request, slug):
    """View for league-specific ladder """
    active_league = get_object_or_404(PoeLeague, slug=slug)
    page = request.GET.get('page', 1)
    query_set = (PoeCharacter.objects.all()
                 .filter(league_id=active_league.id)
                 .order_by('-level', '-experience')
                 .prefetch_related('gems')
                 .select_related('profile'))

    class_filter = PoeCharacterFilter(request.GET, query_set)
    current_profile = request.user.discorduser.poe_profile if hasattr(
        request.user, 'discorduser') else None

    paginator = Paginator(class_filter.qs, 15)
    try:
        characters = paginator.page(page)
    except PageNotAnInteger:
        characters = paginator.page(1)
    except EmptyPage:
        characters = paginator.page(paginator.num_pages)

    if not characters:
        for choice in class_filter.form.fields['class_id'].choices:
            if choice[0] == int(class_filter.form.cleaned_data['class_id']):
                class_filter.__dict__['class_name'] = choice[1]

    return render(request, 'poeladder/ladder.html', {
        'active_league': active_league,
        'class_filter': class_filter,
        'current_profile': current_profile,
        'characters': characters
    })


def search(request):
    """View for cross-league character search by name"""
    response = {'search': True, 'title': 'Search results'}
    page = request.GET.get('page', 1)
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            name = form.cleaned_data['name']
            response['search_query'] = request.GET['name'] if name \
                else 'All characters'
            response['search_results'] = (PoeCharacter.objects
                                          .filter(name__icontains=name)
                                          .order_by('name')
                                          .prefetch_related('gems')
                                          .select_related('profile'))
            paginator = Paginator(response['search_results'], 10)
            try:
                characters = paginator.page(page)
            except PageNotAnInteger:
                characters = paginator.page(1)
            except EmptyPage:
                characters = paginator.page(paginator.num_pages)
            response['characters'] = characters

    return render(request, 'poeladder/ladder.html', response)
