from django.shortcuts import render
from django import get_version
from django.http import JsonResponse
import platform

# Create your views here.
def home_view(request):
    django_version = get_version()
    python_version = platform.python_version
    return render(request, 'home_page_app/home.html', {'django' : django_version, 'python' : python_version})
