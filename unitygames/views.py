from django.shortcuts import render

# Create your views here.
def asteroids(request):
    return render(request, 'unitygames/index.html')