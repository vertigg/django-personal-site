from django.urls import path
from django.views.generic.base import TemplateView

from main.views import (
    DisconnectDiscordAccountView, HomeView, MainLoginView, MainLogoutView,
    ProfileView, SignupView
)

app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', MainLoginView.as_view(), name='login'),
    path('logout/', MainLogoutView.as_view(), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/disconnect', DisconnectDiscordAccountView.as_view(), name='discord_disconnect'),
    path('jovka/', TemplateView.as_view(template_name='jovka.html'), name='jovka'),
    path('calamity/pre-hardmode', TemplateView.as_view(template_name='calamity/pre-hardmode.html'), name='pre-hardmode'),
    path('calamity/hardmode', TemplateView.as_view(template_name='calamity/hardmode.html'), name='hardmode'),
    path('calamity/post-hardmode', TemplateView.as_view(template_name='calamity/post-hardmode.html'), name='post-hardmode'),
]
