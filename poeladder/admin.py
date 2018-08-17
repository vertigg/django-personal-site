from django.contrib import admin
from django.db import models
from django.forms import TextInput
from poeladder.models import PoeCharacter, PoeLeague, PoeActiveGem


class PoeCharacterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'class_name', 'level', 'league')
    search_fields = ('name',)
    list_filter = ('league',)

    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': 20})},
        models.CharField: {'widget': TextInput(attrs={'size': 20})},
    }


class PoeLeagueAdmin(admin.ModelAdmin):
    pass


admin.site.register(PoeCharacter, PoeCharacterAdmin)
admin.site.register(PoeActiveGem)
admin.site.register(PoeLeague)
