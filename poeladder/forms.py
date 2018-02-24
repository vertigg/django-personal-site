from django import forms

class SearchForm(forms.Form):
    """PoE ladder search form"""
    name = forms.CharField(
        required=False, 
        max_length=25, 
        widget=forms.TextInput(attrs={
            'class' : 'poe-search-input', 
            'placeholder' : "Search by name"}
            )
        )