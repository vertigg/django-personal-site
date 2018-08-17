from django.shortcuts import render


def asteroids(request):
    return render(request, 'unitygames/index.html')
