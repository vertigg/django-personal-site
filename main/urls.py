from django.contrib.auth.views import TemplateView
from django.urls import path

from main.views import (
    CalamityHardmodeSetups, CalamityPostHardmodeSetups,
    CalamityPreHardmodeSetups, DisconnectDiscordAccountView, HomeView,
    MainLoginView, MainLogoutView, ProfileView, SignupView
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
    path('calamity/pre-hardmode', CalamityPreHardmodeSetups.as_view(), name='pre-hardmode'),
    path('calamity/hardmode', CalamityHardmodeSetups.as_view(), name='hardmode'),
    path('calamity/post-hardmode', CalamityPostHardmodeSetups.as_view(), name='post-hardmode'),
]
