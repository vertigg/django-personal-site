from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from poe.models import Character, League
from poe.serializers import CharacterSerializer, LeagueSerializer
from poe.utils.session import requests_retry_session


class CharacterViewSet(viewsets.ReadOnlyModelViewSet):
    """Return a list of all existing characters in ladder"""
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('class_id', 'league')
    search_fields = ('name',)
    ordering_fields = ('level',)


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer


class StashHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_stash_history(self, from_date, to_dote):
        pass

    def post(self, request, *args, **kwargs):
        pass
