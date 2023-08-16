from django_filters import CharFilter, FilterSet

from poe.models import Character


class PoeSearchFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Character
        fields = ('name',)
