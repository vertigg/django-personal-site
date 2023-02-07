from django import forms
from django.db.models.fields import BooleanField

from discordbot.deprecated.models import WFSettings


class WFSettingsForm(forms.ModelForm):
    success_message = 'Warframe alerts settings has been updated'

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = WFSettings
        fields = '__all__'
        widgets = {
            x.attname: forms.CheckboxInput(attrs={'class': 'custom-control-input'})
            for x in model._meta.fields if isinstance(x, BooleanField)
        }

    def save(self, commit=True):
        if self.user.discorduser and not self.user.discorduser.wf_settings:
            obj = super().save(commit=commit)
            self.user.discorduser.wf_settings = obj
            self.user.discorduser.save()
            return obj
        return super().save(commit=commit)
