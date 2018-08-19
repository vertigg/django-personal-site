from django.contrib import admin
from django.db import models
from django.forms import TextInput
from wowstats.models import WOWAccount, WOWCharacter, WOWStatSnapshot, PVPBracket


class WOWAccountrAdmin(admin.ModelAdmin):
    list_display = ('user', 'btag', 'bnet_id', 'token', 'register_date')
    search_fields = ('btag',)

    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': 20})},
        models.CharField: {'widget': TextInput(attrs={'size': 20})},
    }


admin.site.register(WOWAccount, WOWAccountrAdmin)
admin.site.register(WOWCharacter)
admin.site.register(WOWStatSnapshot)
admin.site.register(PVPBracket)  # Remove in prod
