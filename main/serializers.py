from rest_framework import serializers
from poeladder.models import PoeCharacter

class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoeCharacter
        fields = ('name', 'class_name', 'level', 'league', )