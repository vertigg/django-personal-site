from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """Connects socialaccount to existing user if email is already in the 
        system
        """
        user = sociallogin.user
        if user.id:
            return
        try:
            user_model = get_user_model()
            if user.email:
                email_user = user_model.objects.get(email=user.email)
                sociallogin.connect(request, email_user)
            elif request.user:
                sociallogin.connect(request, request.user)
        except:
            pass
