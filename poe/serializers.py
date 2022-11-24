from rest_framework import serializers

from poe.models import Character, League


class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ('id', 'name', 'class_name', 'class_id', 'level', 'league',)


class LeagueSerializer(serializers.ModelSerializer):

    class Meta:
        model = League
        fields = ('id', 'name', 'url', 'start_date', 'end_date')


class StashHistoryRange(serializers.Serializer):
    from_date = serializers.IntegerField()
    end_date = serializers.IntegerField()
