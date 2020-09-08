from discordbot.models import DiscordUser
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from allauth.socialaccount.adapter import get_adapter as get_account_adapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """Connects socialaccount to existing user if email is already in the 
        system
        """
        user = sociallogin.user
        if user.id:
            return
        User = get_user_model()
        if user.email:
            try:
                existing_user = User.objects.get(email=user.email)
                sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                pass
        if sociallogin.account.provider == 'discord':
            uid = int(sociallogin.account.uid)
            try:
                existing_discord_user = DiscordUser.objects.get(id=uid)
                existing_discord_user.user = sociallogin.user
                # sociallogin.user.discorduser = existing_discord_user
            except DiscordUser.DoesNotExist:
                pass
        if request.user.id:
            sociallogin.connect(request, request.user)

    def is_open_for_signup(self, request, sociallogin):
        return True

    def save_user(self, request, sociallogin, form):
        user = super().save_user(request, sociallogin, form)
        if sociallogin.account.provider == 'discord':
            uid = int(sociallogin.account.uid)
            try:
                existing_discord_user = DiscordUser.objects.get(id=uid)
                user.discorduser = existing_discord_user
                user.save()
            except DiscordUser.DoesNotExist:
                pass
        return user
