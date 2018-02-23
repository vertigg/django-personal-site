from django.contrib import admin
from .models import PoeCharacter, PoeLeague

class PoeCharacterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'class_name', 'level', 'league')

class PoeLeagueAdmin(admin.ModelAdmin):
    pass

admin.site.register(PoeCharacter, PoeCharacterAdmin)
admin.site.register(PoeLeague)