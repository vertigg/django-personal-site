from poeladder.models import PoeCharacter
from VertigoProject.serializers import CharacterSerializer
from rest_framework import viewsets

class CharacterViewSet(viewsets.ModelViewSet):
    queryset = PoeCharacter.objects.all()
    serializer_class = CharacterSerializer
