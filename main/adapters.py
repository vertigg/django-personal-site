from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse

from discordbot.models import DiscordUser


class CustomDiscordAccountAdapter(DefaultSocialAccountAdapter):

    def authentication_error(self, request, provider_id, **kwargs):
        raise ImmediateHttpResponse(HttpResponseRedirect(reverse('main:login')))

    def pre_social_login(self, request, sociallogin: SocialLogin):
        """
        Connects social account to existing user if email exists in the system
        """
        if sociallogin.account.provider != 'discord' or sociallogin.is_existing:
            return

        # If user already logged in - connect to current account
        if request.user.id:
            sociallogin.connect(request, request.user)
            self.connect_existing_discord_account(request.user, sociallogin)
            return

        # If user already exists and doesn't have discordbot user connected
        if sociallogin.user.id and not hasattr(sociallogin.user, 'discorduser'):
            self.connect_existing_discord_account(sociallogin.user, sociallogin)
            return

        # Attempt to find existing account with same email
        if sociallogin.user.email:
            try:
                User = get_user_model()
                existing_user = User.objects.get(email=sociallogin.user.email)
                sociallogin.user = existing_user
                if not sociallogin.is_existing:
                    sociallogin.connect(request, existing_user)
                self.connect_existing_discord_account(existing_user, sociallogin)
            except User.DoesNotExist:
                pass

    def connect_existing_discord_account(self, user, sociallogin):
        uid = int(sociallogin.account.uid)
        try:
            existing_discord_user = DiscordUser.objects.get(id=uid)
            user.discorduser = existing_discord_user
            user.save()
        except DiscordUser.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form):
        user = super().save_user(request, sociallogin, form)
        self.connect_existing_discord_account(user, sociallogin)
        return user

    def get_connect_redirect_url(self, *args):
        return reverse('main:profile')
