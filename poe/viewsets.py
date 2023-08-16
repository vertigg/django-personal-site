from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from poe.models import Character, League
from poe.serializers import (
    CharacterSerializer, LeagueSerializer, StashHistoryRangeSerializer
)
from poe.utils.session import requests_retry_session


class CharacterViewSet(viewsets.ReadOnlyModelViewSet):
    """Return a list of all existing characters in ladder"""
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('league',)  # FIXME: Not showing in API filters
    search_fields = ('name',)
    ordering_fields = ('level', 'level_modified_at')


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer


class StashHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    url = "https://www.pathofexile.com/api/guild/2932/stash/history"

    def _get_stash_history(self, data: dict[str, int]) -> list[dict]:
        entries = []
        params = {'from': data.get('dates')[0], 'end': data.get('dates')[1]}
        with requests_retry_session(retries=2) as session:
            while True:
                data = session.get(self.url, params=params).json()
                entries.extend(data.get('entries', []))
                if not data.get('truncated') or data.get('error'):
                    break
                last_entry = entries[-1]
                params['from'] = last_entry.get('time')
                params['fromid'] = last_entry.get('from_id')
        return entries

    def post(self, request):
        serializer = StashHistoryRangeSerializer(data=request.data)
        if serializer.is_valid():
            return Response(data=self._get_stash_history(serializer.data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
