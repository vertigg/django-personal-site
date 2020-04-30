from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (FormView, LoginView, LogoutView,
                                       TemplateView)
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import RedirectView

from discordbot.forms import WFSettingsForm
from discordbot.models import DiscordUser
from main.forms import (DiscordProfileForm, DiscordTokenForm,
                        MainAuthenticationForm, MainUserCreationForm)
from poeladder.models import PoeCharacter


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


class UnlinkDiscordProfile(LoginRequiredMixin, RedirectView):
    pattern_name = 'main:profile'

    def get_redirect_url(self, *args, **kwargs):
        if hasattr(self.request.user, 'discorduser'):
            self.request.user.discorduser.user_id = None
            self.request.user.save()
        return reverse(self.pattern_name)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'
    login_url = '/login/'

    def _link_discord_user(self, request, request_method='POST'):
        form = DiscordTokenForm(getattr(request, request_method))
        if form.is_valid():
            token = form.cleaned_data.get('token')
            try:
                discord_user = DiscordUser.objects.get(token=token)
                discord_user.user = request.user
                request.user.save()
            except ObjectDoesNotExist:
                messages.add_message(request, messages.ERROR, 'Invalid token')

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['is_linked'] = hasattr(request.user, 'discorduser')
        if context['is_linked']:
            context.update({
                'profile_form': DiscordProfileForm(
                    user=request.user, instance=request.user.discorduser),
                'wf_settings_form': WFSettingsForm(
                    instance=request.user.discorduser.wf_settings),
            })
        else:
            if request.GET.get('token'):
                self._link_discord_user(request, request_method='GET')
                return HttpResponseRedirect(reverse_lazy('main:profile'))
            context.update({'token_form': DiscordTokenForm})
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        user = request.user
        if 'token_link' in request.POST:
            self._link_discord_user(request)
        if 'profile_update' in request.POST:
            profile_form = DiscordProfileForm(
                request.POST, user=user, instance=user.discorduser)
            wf_form = WFSettingsForm(
                request.POST, instance=user.discorduser.wf_settings)
            if profile_form.is_valid():
                passed_poe_profile = profile_form.cleaned_data.get('poe_profile')
                if passed_poe_profile is None or passed_poe_profile == '' \
                        or passed_poe_profile != user.discorduser.poe_profile:
                    PoeCharacter.objects.filter(
                        profile=user.discorduser.id).delete()
                profile_form.save()
            if wf_form.is_valid():
                wf_form.save()
            messages.add_message(request, messages.SUCCESS, 'Profile settings has been updated')
        return redirect('main:profile')
