import requests
from django import forms
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
                                       UsernameField, password_validation)
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import ModelForm
from django.forms.widgets import PasswordInput, TextInput
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from discordbot.models import DiscordUser


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
        required=False,
        max_length=20,
        help_text=_("17 characters, digits only."),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class DiscordProfileForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(DiscordProfileForm, self).__init__(*args, **kwargs)
        # self.fields['steam_id'].validators = [RegexValidator(r'^\d{1,17}$')]
        # self.fields['steam_id'].max_length = 17
        self.fields['blizzard_id'].validators = [
            RegexValidator(r"([\w]+)\-([\d]{4,5})$")]

    class Meta:
        model = DiscordUser
        fields = ['blizzard_id', 'poe_profile']
        widgets = {
            'blizzard_id': forms.TextInput(attrs={'class': 'form-control'}),
            'poe_profile': forms.TextInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'poe_profile': "'Character' tab in your profile must be public. Ladder updates every 24 hours"
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
                    ('"{}" profile already exists'.format(profile)))
            else:
                return profile
        if requests.get(check_link.format(profile)).status_code != 200:
            raise ValidationError(("Account name is wrong or private"))
        return profile
