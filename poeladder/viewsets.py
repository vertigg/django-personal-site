from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from poeladder.models import PoeCharacter, PoeLeague
from poeladder.serializers import CharacterSerializer, LeagueSerializer


class CharacterViewSet(viewsets.ReadOnlyModelViewSet):
    """Return a list of all existing characters in ladder"""
    queryset = PoeCharacter.objects.all()
    serializer_class = CharacterSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('class_id', 'league')
    search_fields = ('name',)
    ordering_fields = ('level',)


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PoeLeague.objects.all()
    serializer_class = LeagueSerializer
