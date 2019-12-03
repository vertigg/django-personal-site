from discordbot.models import WFSettings
from django import forms
from django.db.models.fields import BooleanField


class WFSettingsForm(forms.ModelForm):

    class Meta:
        model = WFSettings
        fields = '__all__'
        widgets = {x.attname: forms.CheckboxInput(attrs={'class': 'custom-control-input'})
                   for x in model._meta.fields
                   if isinstance(x, BooleanField)}
