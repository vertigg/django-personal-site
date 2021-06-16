from django import forms
from django.db.models.fields import BooleanField

from discordbot.models import MixPollEntry, WFSettings


class WFSettingsForm(forms.ModelForm):
    success_message = 'Warframe alerts settings has been updated'

    def __init__(self, *args, **kwargs) -> None:
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = WFSettings
        fields = '__all__'
        widgets = {x.attname: forms.CheckboxInput(attrs={'class': 'custom-control-input'})
                   for x in model._meta.fields
                   if isinstance(x, BooleanField)}

    def save(self, commit=True):
        if not self.request.user.discorduser.wf_settings:
            obj = super().save(commit=commit)
            self.request.user.discorduser.wf_settings = obj
            self.request.user.discorduser.save()
            return obj
        return super().save(commit=commit)


class MixPollEntryForm(forms.ModelForm):
    liked = forms.NullBooleanSelect()

    class Meta:
        model = MixPollEntry
        fields = ['user', 'image', 'liked']
        widgets = {
            'user': forms.HiddenInput(),
            'image': forms.HiddenInput(),
            'liked': forms.HiddenInput()
        }

    def save(self, commit: bool = True):
        user = self.cleaned_data.get('user')
        image = self.cleaned_data.get('image')
        obj, created = MixPollEntry.objects.get_or_create(user=user, image=image)
        if not created and obj.liked == self.cleaned_data.get('liked'):
            obj.liked = None
        else:
            obj.liked = self.cleaned_data.get('liked')
        return obj.save(update_fields=['liked'])
