from django.test import TestCase, TransactionTestCase
from django.utils.timezone import now

from discordbot.cogs.utils.formatters import extract_urls
from discordbot.models import MixImage


class DiscordModelsTestCase(TransactionTestCase):

    @classmethod
    def setUpClass(cls):
        for _ in range(10):
            MixImage.objects.create(date=now())

    def test_simple_pid_models(self):
        for _ in range(MixImage.objects.count()):
            MixImage.objects.get_random_entry()
        self.assertEqual(
            MixImage.objects.count(),
            MixImage.objects.filter(pid=1).count()
        )
        # Check if pid resets on next call
        MixImage.objects.get_random_entry()
        self.assertEqual(
            MixImage.objects.filter(pid=1).count(), 1,
            'Only one entry should have pid with value 1'
        )


class UtilsTestCase(TestCase):

    def test_extract_urls(self):
        text = """
            http://127.0.0.1/
            Hello https://test.com/somepic.jpeg,
        """
        res = extract_urls(text)
        self.assertEqual(len(res), 2)
        self.assertEqual(
            res, ['http://127.0.0.1/', 'https://test.com/somepic.jpeg']
        )
