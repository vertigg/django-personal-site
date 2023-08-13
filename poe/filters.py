from django import forms
from django_filters import CharFilter, ChoiceFilter, FilterSet

from poe.models import Character


class PoeClassFilter(FilterSet):

    class_choices = (
        (0, 'Scion'),
        (1, 'Marauder'),
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
            'class': "w-100 p-1 bg-gray-700 rounded-none text-sm",
        }))

    class Meta:
        model = Character
        fields = ['class_id']


class PoeSearchFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Character
        fields = ('name',)
