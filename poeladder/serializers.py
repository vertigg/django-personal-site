from rest_framework import serializers

from poeladder.models import PoeCharacter, PoeLeague


class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoeCharacter
        fields = ('id', 'name', 'class_name', 'class_id', 'level', 'league',)


class LeagueSerializer(serializers.ModelSerializer):

    class Meta:
        model = PoeLeague
        fields = ('id', 'name', 'url', 'start_date', 'end_date')
