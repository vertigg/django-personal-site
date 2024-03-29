from rest_framework import serializers

from poe.models import ActiveGem, Character, Item, League
from poe.templatetags.ladder_extras import level_progress


class ActiveGemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveGem
        fields = ('name', 'icon')


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('name', 'icon')


class CharacterSerializer(serializers.ModelSerializer):

    gems = ActiveGemSerializer(many=True)
    items = ItemSerializer(many=True)

    class Meta:
        model = Character
        fields = (
            'id', 'name', 'class_name', 'level', 'league',
            'life', 'es', 'combined_dps', 'gems', 'items'
        )

    def get_progress(self, instance: Character) -> float:
        return level_progress(instance)


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
