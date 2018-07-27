import platform

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render

from discordbot.forms import WFSettingsForm
from discordbot.models import DiscordUser, WFSettings
from poeladder.models import PoeCharacter
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
    return render(request, 'registration/signup.html', {'form' : form})

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
    user = request.user

    if is_linked:
        if user.discorduser.wf_settings is None:
            user.discorduser.wf_settings = WFSettings.objects.create()
            user.discorduser.save()
        profile_form = DiscordProfileForm(user=request.user, instance=get_profile(request))
        wf_settings_form = WFSettingsForm(instance=get_wfsettings(request))
    else:
        profile_form = None
        wf_settings_form = None

    if request.method == "POST":
        if 'token_link' in request.POST:
            form = DiscordTokenForm(request.POST)
            if form.is_valid():
                clean_token = form.cleaned_data.get('token')
                try:
                    discord_user = DiscordUser.objects.get(token=clean_token)
                    discord_user.user = request.user
                    user.save()
                    return redirect('profile')
                except ObjectDoesNotExist:
                    invalid_token = True
        if 'profile_update' in request.POST:
            form = DiscordProfileForm(request.POST, user=request.user, instance=get_profile(request))
            wf_form = WFSettingsForm(request.POST, instance=get_wfsettings(request))
            if form.is_valid():
                passed_poe_profile = form.cleaned_data.get('poe_profile')
                if passed_poe_profile is None or passed_poe_profile == '' or passed_poe_profile != user.discorduser.poe_profile:
                    PoeCharacter.objects.filter(profile=user.discorduser.id).delete()
                form.save()
                is_updated = True
                profile_form = DiscordProfileForm(request.POST, user=request.user, instance=get_profile(request))
            else:
                profile_form = form
            if wf_form.is_valid():
                wf_form.save()
                wf_settings_form = WFSettingsForm(request.POST, instance=get_wfsettings(request))
    
    return render(request, 'profile.html', {
        'is_linked' : is_linked,
        'token_form' : token_form,
        'profile_form' : profile_form,
        'invalid_token' : invalid_token,
        'wf_settings_form' : wf_settings_form,
        'update_success' : is_updated
        })


def get_wfsettings(request):
    return request.user.discorduser.wf_settings

def get_profile(request):
    return request.user.discorduser
    