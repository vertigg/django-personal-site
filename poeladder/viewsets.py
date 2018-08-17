from poeladder.models import PoeCharacter
from poeladder.serializers import CharacterSerializer
from rest_framework import viewsets

class CharacterViewSet(viewsets.ModelViewSet):
    """
    Return a list of all existing characters in ladder
    """
    queryset = PoeCharacter.objects.all()
    serializer_class = CharacterSerializer
