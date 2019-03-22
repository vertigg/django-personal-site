from django.urls import path
from django.contrib.auth.views import TemplateView

urlpatterns = [
    path('dots/', TemplateView.as_view(template_name='dots.html'), name='dots'),
    path('asteroids/',
         TemplateView.as_view(template_name='webgames/index.html'), name='asteroids'),
]
