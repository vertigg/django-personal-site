from poeladder.models import PoeCharacter
from main.serializers import CharacterSerializer
from rest_framework import viewsets

class CharacterViewSet(viewsets.ModelViewSet):
    queryset = PoeCharacter.objects.all()
    serializer_class = CharacterSerializer
