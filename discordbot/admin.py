from django.contrib import admin
from django.forms import TextInput, Textarea, NumberInput
from django.db import models
from discordbot.models import Wisdom, DiscordUser, Gachi, DiscordSettings, DiscordLink, WFAlert
from django.template.defaultfilters import truncatechars


class DiscordLinkAdmin(admin.ModelAdmin):
    list_display = ('key', 'url')
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 20})},
    }


class DiscordSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')


class WisdomAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'short_text')
    list_filter = ('date',)
    search_fields = ('text',)
    fields = ('author', 'text', 'date')
    readonly_fields = ('date',)

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 150})},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            kwargs["queryset"] = DiscordUser.objects.filter(mod_group=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def short_text(self, obj):
        return truncatechars(obj.text, 100)


class DiscordUserAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'id', "admin", "mod_group")
    search_fields = ('display_name',)
    list_filter = ('admin', 'mod_group',)
    fields = ('display_name', 'id', 'steam_id', 'blizzard_id',
              'poe_profile', 'admin', 'mod_group', 'user', 'wf_settings')

    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': 20})},
        models.CharField: {'widget': TextInput(attrs={'size': 20})},
    }


class GachiAdmin(admin.ModelAdmin):
    fields = ('url',)


admin.site.register(Wisdom, WisdomAdmin)
admin.site.register(DiscordUser, DiscordUserAdmin)
admin.site.register(Gachi, GachiAdmin)
admin.site.register(DiscordSettings, DiscordSettingsAdmin)
admin.site.register(DiscordLink, DiscordLinkAdmin)
admin.site.register(WFAlert)
