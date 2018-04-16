import requests
from django import forms
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
                                       UsernameField, password_validation)
from django.core.validators import RegexValidator
from django.forms.widgets import PasswordInput, TextInput
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

class StyledAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        max_length=254,
        widget=TextInput(attrs={'class':'form-control'}),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=PasswordInput(attrs={'class':'form-control'})
    )

class StyledUserCreationForm(UserCreationForm):
    username = forms.CharField(widget=TextInput(attrs={'class':'form-control'}))
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

class DiscordTokenForm(forms.Form):
    token = forms.CharField(
        required=False,
        max_length=20,
        help_text=_("17 characters, digits only."),
        widget=forms.TextInput(attrs={'class':'form-control'})
    )

class DiscordProfileForm(forms.Form):

    steam_id = forms.CharField(
        label= _("Steam ID"),
        required=False,
        max_length=17,
        validators=[RegexValidator(r'^\d{1,17}$')], 
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text=mark_safe("17 characters, digits only. <a href='https://steamid.io/'>Find your SteamID64</a>")
    )

    blizzard_id = forms.CharField (
        label =_("Blizzard ID"),
        required=False,
        validators=[RegexValidator(r"([\w]+)\-([\d]{4,5})$")],
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text="Example: Username-0000"
    )

    poe_profile = forms.CharField (
        label =_("Path of Exile Profile"),
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text="'Character' tab must be public"
    )

    def clean_poe_profile(self):
        profile_passed = self.cleaned_data.get('poe_profile')
        check_link = 'https://pathofexile.com/character-window/get-characters?accountName={}'
        if profile_passed is None or profile_passed == '':
            return profile_passed
        if requests.get(check_link.format(profile_passed)).status_code != 200:
            raise ValidationError(("Account name is wrong or private".format(profile_passed)))
        return profile_passed