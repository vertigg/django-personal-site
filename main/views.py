from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import FormView

from main.forms import MainAuthenticationForm, MainUserCreationForm


class HomeView(TemplateView):
    template_name = 'home.html'


class MainLoginView(LoginView):
    authentication_form = MainAuthenticationForm
    redirect_authenticated_user = True


class MainLogoutView(LogoutView):
    next_page = 'main:home'


class SignupView(FormView):
    form_class = MainUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('main:home')

    def get_success_url(self):
        if self.request.GET.get('next'):
            return self.request.GET.get('next')
        return super().get_success_url()

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(self.request, user)
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    """Simple profile view"""
    login_url = '/login/'
    template_name = 'profile.html'


class DisconnectDiscordAccountView(RedirectView):
    pattern_name = 'main:profile'

    def post(self, request, *args, **kwargs):
        request.user.socialaccount_set.filter(provider='discord').delete()
        if hasattr(request.user, 'discorduser'):
            discorduser = request.user.discorduser
            discorduser.user = None
            discorduser.save()
        messages.success(request, 'Discord account disconnected')
        return super().post(request, *args, **kwargs)
