from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

from discordbot.models import DiscordUser


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Connects socialaccount to existing user if email exists in the system
        """
        user = sociallogin.user
        if user.id:
            return
        # If user have an email in the system - connect to this account
        if user.email:
            try:
                User = get_user_model()
                existing_user = User.objects.get(email=user.email)
                sociallogin.connect(request, existing_user)
                raise ImmediateHttpResponse(redirect('main:profile'))
            except User.DoesNotExist:
                pass
        # If user already logged in - connect to current account
        if request.user.id:
            sociallogin.connect(request, request.user)

    def save_user(self, request, sociallogin, form):
        user = super().save_user(request, sociallogin, form)
        # Try to connect existing DiscordUser instance if available
        # Otherwise user will be promted to connect with DiscordUser manually
        # via profile
        if sociallogin.account.provider == 'discord':
            uid = int(sociallogin.account.uid)
            try:
                existing_discord_user = DiscordUser.objects.get(id=uid)
                user.discorduser = existing_discord_user
                user.save()
            except DiscordUser.DoesNotExist:
                pass
        return user
