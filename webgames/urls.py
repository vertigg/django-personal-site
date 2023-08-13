from django.urls import path
from django.views.generic.base import TemplateView

urlpatterns = [
    path('dots/', TemplateView.as_view(template_name='dots/index.html'), name='dots'),
    path('asteroids/', TemplateView.as_view(template_name='asteroids/index.html'), name='asteroids'),
]
