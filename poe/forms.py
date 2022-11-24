from django import forms


class SearchForm(forms.Form):
    """PoE ladder search form"""
    name = forms.CharField(
        required=False,
        max_length=25,
        widget=forms.TextInput(attrs={
            'class': 'form-control poe-search-form mr-sm-2',
            'type': 'text',
            'placeholder': "Search character by name"
        })
    )
