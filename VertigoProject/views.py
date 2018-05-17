import platform

from django import get_version
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render

from discordbot.models import DiscordUser, WFSettings
from discordbot.forms import WFSettingsForm
from VertigoProject.forms import (DiscordProfileForm, DiscordTokenForm,
                                  StyledUserCreationForm)


def home_view(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        form = StyledUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = StyledUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required(login_url='/login/')
def unlink(request):
    if hasattr(request.user, 'discorduser'):
        request.user.discorduser.user_id = None
        request.user.save()
    return redirect('profile')


@login_required(login_url='/login/')
def profile(request):

    is_linked = hasattr(request.user, 'discorduser')
    is_updated = False
    invalid_token = False
    token_form = DiscordTokenForm

    if is_linked:
        if request.user.discorduser.wf_settings is None:
            request.user.discorduser.wf_settings = WFSettings.objects.create()
            request.user.discorduser.save()

        profile_form = DiscordProfileForm(initial=get_profile_data(request))
        wf_settings_form = WFSettingsForm(initial=get_wfsettings_data(request))
    else:
        profile_form = DiscordProfileForm
        wf_settings_form = WFSettingsForm

    if request.method == "POST":
        if 'token_link' in request.POST:
            form = DiscordTokenForm(request.POST)
            if form.is_valid():
                clean_token = form.cleaned_data.get('token')
                try:
                    discord_user = DiscordUser.objects.get(token=clean_token)
                    discord_user.user = request.user
                    request.user.save()
                    return redirect('profile')
                except ObjectDoesNotExist:
                    invalid_token = True

        if 'profile_update' in request.POST:
            form = DiscordProfileForm(request.POST)
            form2 = WFSettingsForm(request.POST)
            if form.is_valid() and form2.is_valid():

                request.user.discorduser.steam_id = form.cleaned_data.get('steam_id')
                request.user.discorduser.blizzard_id = form.cleaned_data.get('blizzard_id')
                request.user.discorduser.poe_profile = form.cleaned_data.get('poe_profile')

                wfs = request.user.discorduser.wf_settings
                wf_data = form2.cleaned_data

                wfs.nitain_extract = wf_data.get('nitain_extract')
                wfs.orokin_cell = wf_data.get('orokin_cell')
                wfs.orokin_reactor_bp = wf_data.get('orokin_reactor_bp')
                wfs.orokin_catalyst_bp = wf_data.get('orokin_catalyst_bp')
                wfs.tellurium = wf_data.get('tellurium')
                wfs.forma_bp = wf_data.get('forma_bp')
                wfs.exilus_bp = wf_data.get('exilus_bp')
                wfs.exilus_ap = wf_data.get('exilus_ap')
                wfs.kavat = wf_data.get('kavat')
                wfs.corrosive = wf_data.get('corrosive')
                
                wfs.save()
                request.user.save()
                if request.POST.get('update'):
                    is_updated = True
                profile_form = DiscordProfileForm(initial=get_profile_data(request))
                wf_settings_form = WFSettingsForm(initial=get_wfsettings_data(request))
            else:
                profile_form = form
    
    return render(request, 'profile.html', {
        'is_linked' : is_linked,
        'token_form' : token_form,
        'profile_form' : profile_form,
        'invalid_token' : invalid_token,
        'wf_settings_form' : wf_settings_form,
        'update_success' : is_updated
        })


def get_wfsettings_data(request):
    wfs = request.user.discorduser.wf_settings
    initial_wfsettings = {
                        'nitain_extract' : wfs.nitain_extract,
                        'orokin_cell' : wfs.orokin_cell,
                        'orokin_reactor_bp' : wfs.orokin_reactor_bp,
                        'orokin_catalyst_bp' : wfs.orokin_catalyst_bp,
                        'tellurium' : wfs.tellurium,
                        'forma_bp' : wfs.forma_bp,
                        'exilus_bp' : wfs.exilus_bp,
                        'exilus_ap' : wfs.exilus_ap,
                        'kavat' : wfs.kavat,
                        'corrosive' : wfs.corrosive,
                        }
    return initial_wfsettings

def get_profile_data(request):
    initian_profile_data = {
            'steam_id' : request.user.discorduser.steam_id,
            'blizzard_id' : request.user.discorduser.blizzard_id,
            'poe_profile' : request.user.discorduser.poe_profile,
            }
    return initian_profile_data           