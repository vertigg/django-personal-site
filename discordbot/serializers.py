from rest_framework import serializers
from discordbot.models import CoronaReport


class CoronaReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoronaReport
        fields = ('confirmed', 'recovered', 'deaths')
