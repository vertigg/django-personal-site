from django.urls import path

from main.views import (DiscordLinkView, DiscorUnlinkView, HomeView,
                        MainLoginView, MainLogoutView, ProfileView, SignupView)

app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', MainLoginView.as_view(), name='login'),
    path('logout/', MainLogoutView.as_view(), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('link/', DiscordLinkView.as_view(), name='discord_link'),
    path('unlink/', DiscorUnlinkView.as_view(), name='unlink'),
]
