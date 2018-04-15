import platform

from django import get_version
from django.contrib.auth import authenticate, login
from VertigoProject.forms import StyledUserCreationForm
from django.http import JsonResponse
from django.shortcuts import redirect, render


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