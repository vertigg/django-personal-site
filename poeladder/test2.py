'''
External script for populating/updating
poeladder app related tables
'''

import json
import os
import sys
import time

import requests

POE_LEAGUES = 'http://api.pathofexile.com/leagues?type=main&compact=1'
POE_PROFILE = 'https://www.pathofexile.com/character-window/get-characters?accountName={}'

#sys.path.append('C:\\Users\\EpicVertigo\\Desktop\\')
print(os.path.join(os.path.dirname(__file__), 'DjangoEnv\Lib\\site-packages'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'DjangoEnv\Lib\\site-packages'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'VertigoProject.settings'
import django
django.setup()

# import models after django.setup()
from discordbot.models import DiscordUser
from poeladder.models import PoeLeague, PoeCharacter

def update_ladders_table():
    try:
        leagues_data = json.loads(requests.get(POE_LEAGUES).text)
        PoeLeague.objects.get_or_create(name='Void')
        for league in leagues_data:
            l, created = PoeLeague.objects.get_or_create(
                name = league['id'],
                )
            l.start_date = league['startAt']
            l.url = league['url']
            l.end_date = league['endAt']
            l.save(update_fields=['url', 'start_date', 'end_date'])
    except Exception as e:
        pass


def update_characters_table():
    query = DiscordUser.objects.exclude(poe_profile__exact='')
    poe_profiles = {x.id : x.poe_profile for x in query}

    try:
        for k,v in poe_profiles.items():
            print('{0} - {1}'.format(k,v))
            r = requests.get(POE_PROFILE.format(v))
            characters = json.loads(r.text)
            if characters:
                for character in json.loads(r.text):
                    print(character)
                    p, created = PoeCharacter.objects.get_or_create(
                        name = character['name'],
                        league = PoeLeague.objects.get(name=character['league']),
                        profile = DiscordUser.objects.get(id=k)
                        )

                    p.ascendancy = character['class']
                    p.level = character['level']

                    p.save(update_fields=['league','ascendancy','level'])
    except Exception as e:
        pass


def get_character_exp():
    pass

if __name__ == '__main__':
    update_characters_table()
    update_characters_table()