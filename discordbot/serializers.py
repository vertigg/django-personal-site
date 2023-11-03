from rest_framework import serializers
from discordbot.models import MixImage


class MixImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = MixImage
        fields = ('image', 'author', 'date', 'url', 'checksum', 'deleted')
