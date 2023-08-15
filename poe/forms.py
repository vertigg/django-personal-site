from django import forms


class SearchForm(forms.Form):
    """PoE ladder search form"""
    name = forms.CharField(
        required=False,
        max_length=25,
        widget=forms.TextInput(attrs={
            'class': 'h-6 p-2 rounded-md text-sm text-black placeholder:text-xs',
            'type': 'text',
            'placeholder': "Search character by name"
        })
    )
