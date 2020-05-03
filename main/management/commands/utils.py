import logging
import time

from django.core.management.base import BaseCommand


class AdvancedCommand(BaseCommand):
    _logger = None
    logger_name = 'management_command'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        self.start_time = time.time()
        super().__init__(stdout=stdout, stderr=stderr, no_color=no_color, force_color=force_color)

    @property
    def execution_time(self) -> float:
        """Returns current execution time in seconds"""
        return round(time.time() - self.start_time, 2)

    @property
    def logger(self) -> logging.Logger:
        if not self._logger:
            self._logger = self._setup_management_logger()
        return self._logger

    def log_execution_time(self):
        self.logger.info(f'Done in {self.execution_time} seconds')

    def _setup_management_logger(self):
        logger = logging.getLogger(self.logger_name)
        return logger
