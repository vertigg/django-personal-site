from django.contrib import admin
from django.db import models
from django.forms import TextInput
from poeladder.models import PoeCharacter


class PoeCharacterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'class_name', 'level', 'league')
    search_fields = ('name',)
    list_filter = ('league',)

    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': 20})},
        models.CharField: {'widget': TextInput(attrs={'size': 20})},
    }


admin.site.register(PoeCharacter, PoeCharacterAdmin)
