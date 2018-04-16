import platform

from django import get_version
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render

from discordbot.models import DiscordUser
from VertigoProject.forms import (DiscordProfileForm, DiscordTokenForm,
                                  StyledUserCreationForm)


def home_view(request):
    django_version = get_version()
    python_version = platform.python_version
    return render(request, 'home.html', {'django' : django_version, 'python' : python_version})

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
    invalid_token = False
    token_form = DiscordTokenForm
    if is_linked:
        profile_form = DiscordProfileForm(initial={
            'steam_id' : request.user.discorduser.steam_id,
            'blizzard_id' : request.user.discorduser.blizzard_id,
            'poe_profile' : request.user.discorduser.poe_profile,
            })
    else:
        profile_form = DiscordProfileForm

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
            if form.is_valid():
                request.user.discorduser.steam_id = form.cleaned_data.get('steam_id')
                request.user.discorduser.blizzard_id = form.cleaned_data.get('blizzard_id')
                request.user.discorduser.poe_profile = form.cleaned_data.get('poe_profile')
                request.user.save()
                return redirect('profile')
            else:
                profile_form = form

    
    return render(request, 'profile.html', {
        'is_linked' : is_linked,
        'token_form' : token_form,
        'profile_form' : profile_form,
        'invalid_token' : invalid_token,
        })
