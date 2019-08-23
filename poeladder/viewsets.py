from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from poeladder.models import PoeCharacter
from poeladder.serializers import CharacterSerializer


class CharacterViewSet(viewsets.ModelViewSet):
    """Return a list of all existing characters in ladder"""
    queryset = PoeCharacter.objects.all()
    serializer_class = CharacterSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('class_id', 'league')
    search_fields = ('name',)
    ordering_fields = ('level',)
