from django.urls import path
from main.views import (HomeView, MainLoginView, MainLogoutView, SignupView,
                        UnlinkDiscordProfile, profile_view)

app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', MainLoginView.as_view(), name='login'),
    path('logout/', MainLogoutView.as_view(), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('profile/', profile_view, name='profile'),
    path('unlink/', UnlinkDiscordProfile.as_view(), name='unlink'),
]
