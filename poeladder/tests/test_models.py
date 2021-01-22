from django.test import TestCase
from django.utils.text import slugify
from poeladder.models import PoeLeague


class PoeLeagueTestCase(TestCase):

    def setUp(self):
        self.test_name = "fwqjj-12515kafd-1"
        self.test_obj = PoeLeague.objects.create(name=self.test_name)
        return super().setUp()

    def test_poe_league_slug_creation(self):
        """Slug must be created from 'name' field after creation"""
        self.assertEqual(self.test_obj.slug, slugify(self.test_name))

    def test_renaming_slug(self):
        """Slug should stay the same after changing 'name' field"""
        self.test_obj.name = "monkaS"
        self.test_obj.save()
        self.assertEqual(self.test_obj.slug, slugify(self.test_name))
