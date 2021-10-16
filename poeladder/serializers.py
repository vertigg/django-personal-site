from rest_framework import serializers
from poeladder.models import PoeCharacter


class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoeCharacter
        fields = ('id', 'name', 'class_name', 'class_id', 'level', 'league',)
