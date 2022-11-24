from django.contrib import admin

from discordbot.models import DiscordUser
from poe.models import Announcement, Character, League

admin.site.register(Announcement)


class ProfileFilter(admin.SimpleListFilter):
    parameter_name = 'profile'
    title = 'Profile'

    def lookups(self, request, model_admin):
        return list(
            DiscordUser.objects
            .exclude(poe_profile__isnull=True)
            .exclude(poe_profile='')
            .values_list('id', 'poe_profile')
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(profile_id=self.value())


@admin.register(Character)
class PoeCharacterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'class_name', 'level', 'league')
    search_fields = ('name',)
    list_filter = ('league', ProfileFilter)
    exclude = ['gems']

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


@admin.register(League)
class PoeLeagueAdmin(admin.ModelAdmin):
    readonly_fields = ('name', 'start_date', 'end_date', 'slug')
