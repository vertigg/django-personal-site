from poeladder.models import PoeCharacter
from django import forms
import django_filters


class PoeCharacterFilter(django_filters.FilterSet):

    class_choices = (
        (0, 'Scion'),
        (1, 'Maradeur'),
        (2, 'Ranger'),
        (3, 'Witch'),
        (4, 'Duelist'),
        (5, 'Templar'),
        (6, 'Shadow'),
    )
    class_id = django_filters.ChoiceFilter(
        choices=class_choices,
        empty_label='All classes',
        widget=forms.Select(attrs={
            'onchange': 'this.form.submit()',
            'class': "ladder-select",
        }))

    class Meta:
        model = PoeCharacter
        fields = ['class_id']
