import logging

import requests
from django.core.management.base import BaseCommand

from discordbot.models import CoronaReport
from discordbot.serializers import CoronaReportSerializer


class Command(BaseCommand):
    help = 'Updates Corona reports'
    url = CoronaReport.get_api_url()

    def __init__(self, *args, **kwargs):
        self.logger = self._setup_logger()
        super().__init__(self, args, kwargs)

    def _setup_logger(self):
        formatter = logging.Formatter(
            '%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        file_handler = logging.FileHandler('logs/corona_update.log')
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger

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
