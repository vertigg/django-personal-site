from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    FormView, LoginView, LogoutView, TemplateView
)
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView

from discordbot.forms import WFSettingsForm
from main.forms import (
    DiscordProfileForm, MainAuthenticationForm, MainUserCreationForm
)


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
    """
    General profile view with two forms - general settings for DiscordUser and
    Warframe settings. For now it requires User to be linked with DiscordUser
    instance.
    """
    login_url = '/login/'
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not any(context.get(x) for x in ('profile_form', 'wf_settings_form')):
            profile_form = DiscordProfileForm(
                user=self.request.user,
                instance=getattr(self.request.user, 'discorduser', None)
            )
            context.update({'profile_form': profile_form})
            if profile_form.instance and profile_form.instance.id:
                context.update({
                    'wf_settings_form': WFSettingsForm(
                        instance=self.request.user.discorduser.wf_settings or None
                    ),
                })
        return context

    def post(self, request):
        profile_form = DiscordProfileForm(
            data=request.POST, user=request.user,
            instance=request.user.discorduser
        )
        wf_form = WFSettingsForm(
            data=request.POST,
            instance=request.user.discorduser.wf_settings,
            user=request.user
        )
        for form in (profile_form, wf_form):
            if form.has_changed() and form.is_valid():
                form.save()
                messages.success(request, form.success_message)
        return self.render_to_response({
            'profile_form': profile_form,
            'wf_settings_form': wf_form,
        })


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
