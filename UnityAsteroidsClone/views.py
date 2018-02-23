from django.shortcuts import render

# Create your views here.
def asteroids_view(request):
    return render(request, 'unity_asteroids_app/index.html')