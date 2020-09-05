from discordbot.models import WFSettings
from django import forms
from django.db.models.fields import BooleanField


class WFSettingsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs) -> None:
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = WFSettings
        fields = '__all__'
        widgets = {x.attname: forms.CheckboxInput(attrs={'class': 'custom-control-input'})
                   for x in model._meta.fields
                   if isinstance(x, BooleanField)}

    def save(self, commit=True, **kwargs):
        if not self.request.user.discorduser.wf_settings:
            obj = super().save(commit=commit)
            self.request.user.discorduser.wf_settings = obj
            self.request.user.discorduser.save()
            return obj
        return super().save(commit=commit)
