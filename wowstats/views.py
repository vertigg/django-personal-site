from django.shortcuts import render, get_object_or_404, redirect
import requests_oauth2.services
from requests_oauth2 import OAuth2
import requests
import json
from django.views.generic.base import TemplateView


class Blizzard(OAuth2):
    client_id = '5rs43zuznj52wfn9sb9nz785ctgqtmdw'
    client_secret = '74k2uv9DCjnqgBJ2CSNhjvJtKexCKsY9'
    token_url = 'oauth/token'
    redirect_uri = 'https://www.epicvertigo.xyz/wow/bnet'
    site = 'https://eu.battle.net/'
    scope_sep = [' ']


client = Blizzard()


def main(request):
    authorization_url = None
    token = request.user.discorduser.bnet_token
    print(token)
    if token:
        authorized = True
    else:
        authorized = False
        authorization_url = client.authorize_url(
            scope='wow.profile',
            response_type="code",
        )
    return render(request, 'wow_main.html', {
        'authorized': authorized,
        'authorization_url': authorization_url,
    })


class CharactersView(TemplateView):
    template_name = 'hero_view.html'

    def get_context_data(self, **kwargs):
        context = super(CharactersView, self).get_context_data(**kwargs)
        context['data'] = self.get_characters()
        return context

    def get_characters(self):
        token = self.request.user.discorduser.bnet_token

        url = "https://eu.api.battle.net/wow/user/characters/"
        headers = {
            'Content-Type': "application/json",
            'Authorization': "Bearer {}".format(token),
            'Cache-Control': "no-cache",
        }
        response = requests.request("GET", url, headers=headers)
        return json.loads(response.text)


def callback(request):
    print(client)
    code = '5rt66bzv8mxp75p2fmkph35d'
    data = client.get_token(code=code, grant_type="authorization_code")
    print(data)
    # if data:
    #     discord_user = request.user.discorduser
    #     discord_user.bnet_token = data['access_token']
    #     discord_user.save()
    #     return redirect('profile')
    # else:
    return redirect('home')
