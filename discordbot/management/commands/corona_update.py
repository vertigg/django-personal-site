import requests

from discordbot.models import CoronaReport
from discordbot.serializers import CoronaReportSerializer
from main.management.commands.utils import AdvancedCommand


class Command(AdvancedCommand):
    help = 'Updates Corona reports'
    url = CoronaReport.get_api_url()

    def update(self):
        response = requests.get(self.url).json()
        data = response['features'][0]['attributes']
        serializer = CoronaReportSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            self.logger.error(serializer.errors)

    def handle(self, *args, **options):
        self.logger.info('Updating Corona virus data')
        self.update()
        self.log_execution_time()
