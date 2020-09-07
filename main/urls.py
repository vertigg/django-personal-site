from django.urls import path

from main.views import (HomeView, MainLoginView, MainLogoutView, ProfileView, SignupView)

app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', MainLoginView.as_view(), name='login'),
    path('logout/', MainLogoutView.as_view(), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
