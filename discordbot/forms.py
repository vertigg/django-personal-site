from django.forms import ModelForm
from discordbot.models import WFSettings
from django import forms
from django.utils.translation import gettext_lazy as _

class WFSettingsForm(forms.ModelForm):

    class Meta:
        model = WFSettings
        fields = '__all__'
        
        widgets = {
            'nitain_extract' : forms.CheckboxInput(attrs={'class':'custom-control-input'}),
            'orokin_cell' : forms.CheckboxInput(attrs={'class':'custom-control-input'}),
            'orokin_reactor_bp' : forms.CheckboxInput(attrs={'class':'custom-control-input'}),
            'orokin_catalyst_bp' : forms.CheckboxInput(attrs={'class':'custom-control-input'}),
            'tellurium' : forms.CheckboxInput(attrs={'class':'custom-control-input'}),
            'forma_bp' : forms.CheckboxInput(attrs={'class':'custom-control-input'}),
            'exilus_ap' : forms.CheckboxInput(attrs={'class':'custom-control-input'}),
            'kavat' : forms.CheckboxInput(attrs={'class':'custom-control-input'}),
        }

        labels = {
            'nitain_extract' : _('Nitain Extract'),
            'orokin_cell': _('Orokin Cell'),
            'orokin_reactor_bp': _('Orokin Reactor (Blueprint)'),
            'orokin_catalyst_bp': _('Orokin Catalyst (Blueprint)'),
            'forma_bp': _('Forma or Forma Blueprint'),
            'exilus_ap': _('Exilus Adapter'),
            'kavat': _('Kavat Genetic Code'),
        }