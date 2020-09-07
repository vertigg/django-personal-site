import requests
from django import forms
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
                                       UsernameField, password_validation)
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import ModelForm
from django.forms.widgets import PasswordInput, TextInput
from django.utils.translation import gettext_lazy as _

from discordbot.models import DiscordUser
from poeladder.models import PoeCharacter


class MainAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        max_length=254,
        widget=TextInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=PasswordInput(attrs={'class': 'form-control'})
    )


class MainUserCreationForm(UserCreationForm):
    username = forms.CharField(
        widget=TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )


class DiscordTokenForm(forms.Form):
    token = forms.CharField(
        required=True,
        max_length=20,
        help_text=_("20 characters, digits only."),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean_token(self):
        token = self.cleaned_data.get('token')
        if not DiscordUser.objects.filter(token=token).exists():
            raise ValidationError('Invalid token', code='invalid')
        return token

    def link_discord_profile(self, user):
        token = self.cleaned_data.get('token')
        try:
            discord_user = DiscordUser.objects.get(token=token)
            discord_user.user = user
            user.save()
        except DiscordUser.DoesNotExist:
            raise ValidationError('Discord user is missing', code='missing_discord_user')


class DiscordProfileForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(DiscordProfileForm, self).__init__(*args, **kwargs)

    class Meta:
        model = DiscordUser
        fields = ('poe_profile',)
        widgets = {
            'poe_profile': forms.TextInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'poe_profile': ("'Character' tab in your profile must be public. "
                            "Ladder updates every 24 hours")
        }
        labels = {'poe_profile': _("Path of Exile Profile")}

    def clean_poe_profile(self):
        profile = self.cleaned_data.get('poe_profile')
        check_link = 'https://pathofexile.com/character-window/get-characters?accountName={}'
        if profile is None or profile == '':
            return profile
        if DiscordUser.objects.filter(poe_profile=profile).exists():
            if not self.user.discorduser.poe_profile == profile:
                raise ValidationError(
                    f'"{profile}" profile is already linked to another user'
                )
        if requests.get(check_link.format(profile)).status_code != 200:
            raise ValidationError(
                f'Account name "{profile}" is incorrect or profile is private'
            )
        return profile

    def save(self, commit=True, user=None):
        if user and not self.cleaned_data.get('poe_profile'):
            PoeCharacter.objects.filter(profile=user.discorduser.id).delete()
        return super().save(commit=commit)
