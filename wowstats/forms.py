from django import forms
from wowstats.models import REGIONS


class RegionChoiceForm(forms.Form):
    """Region choice form"""
    name = forms.ChoiceField(
        required=False,
        choices=REGIONS,
    )
