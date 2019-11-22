from datetime import datetime

from django.contrib import admin, messages
from django.db import models
from django.forms import Textarea, TextInput
from django.http import HttpResponseRedirect
from django.template.defaultfilters import truncatechars

from discordbot.models import (
    Counter, CounterGroup, DiscordLink, DiscordSettings, DiscordUser, Gachi,
    MarkovText, WFAlert, Wisdom)


@admin.register(MarkovText)
class MarkovTextAdmin(admin.ModelAdmin):
    list_display = ('key', 'last_update')
    fields = ('key', 'last_update', 'text_length')
    readonly_fields = ('last_update', 'text_length')

    def text_length(self, obj):
        return len(obj.text)

    def response_change(self, request, obj):
        if '_clearobject' in request.POST:
            obj.text = ''
            obj.last_update = datetime(1970, 1, 1)
            obj.save()
            messages.add_message(request, messages.INFO, 'Object has been cleared')
            return HttpResponseRedirect('.')
        return super().response_change(request, obj)


@admin.register(Counter)
class BasicCounterAdmin(admin.ModelAdmin):
    pass


@admin.register(CounterGroup)
class CounterGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(DiscordLink)
class DiscordLinkAdmin(admin.ModelAdmin):
    list_display = ('key', 'url')
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 20})},
    }


@admin.register(DiscordSettings)
class DiscordSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')


@admin.register(Wisdom)
class WisdomAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'short_text')
    list_filter = ('date',)
    search_fields = ('text',)
    fields = ('author', 'text', 'date')
    readonly_fields = ('date',)

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 100})},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            kwargs["queryset"] = DiscordUser.objects.filter(mod_group=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def short_text(self, obj):
        return truncatechars(obj.text, 100)


@admin.register(DiscordUser)
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


@admin.register(Gachi)
class GachiAdmin(admin.ModelAdmin):
    fields = ('url',)


admin.site.register(WFAlert)
