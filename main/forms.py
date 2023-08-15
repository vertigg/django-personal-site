from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm, UsernameField, password_validation
)
from django.forms.widgets import PasswordInput
from django.utils.translation import gettext_lazy as _


class MainAuthenticationForm(AuthenticationForm):
    username = UsernameField(max_length=254)
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=PasswordInput()
    )


class MainUserCreationForm(UserCreationForm):
    username = forms.CharField()
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )
