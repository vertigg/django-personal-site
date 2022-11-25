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


class DatetimeToUnixtimeField(serializers.DateTimeField):

    def to_internal_value(self, value):
        return int(super().to_internal_value(value).timestamp())

    def to_representation(self, value):
        return value


class StashHistoryRangeSerializer(serializers.Serializer):
    dates = serializers.ListField(
        child=DatetimeToUnixtimeField(),
        min_length=2, max_length=2, allow_empty=False
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['dates'] = sorted(attrs.get('dates'), reverse=True)
        return attrs
