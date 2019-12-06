from django import forms
from django_filters import ChoiceFilter, FilterSet, CharFilter

from poeladder.models import PoeCharacter


class PoeClassFilter(FilterSet):

    class_choices = (
        (0, 'Scion'),
        (1, 'Maradeur'),
        (2, 'Ranger'),
        (3, 'Witch'),
        (4, 'Duelist'),
        (5, 'Templar'),
        (6, 'Shadow'),
    )
    class_id = ChoiceFilter(
        choices=class_choices,
        empty_label='All classes',
        widget=forms.Select(attrs={
            'onchange': 'this.form.submit()',
            'class': "ladder-select",
        }))

    class Meta:
        model = PoeCharacter
        fields = ['class_id']


class PoeSearchFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = PoeCharacter
        fields = ('name',)
