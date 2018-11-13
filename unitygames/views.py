from django.shortcuts import render


def asteroids(request):
    return render(request, 'unitygames/index.html')


def dots(request):
    return render(request, 'dots.html')
