from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import mark_safe

from discordbot.models import DiscordUser
from poe.models import Announcement, Character, Item, League
from poe.tasks import CharacterStatsUpdateTask, LadderUpdateTask

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
    exclude = ['gems', 'items']

    class Media:
        css = {'all': ('admin/css/custom.css',)}

    def get_urls(self):
        return [path('ladder_update/', self.ladder_update)] + super().get_urls()

    def ladder_update(self, request):
        LadderUpdateTask.delay()  # pylint: disable=no-value-for-parameter
        messages.add_message(request, messages.INFO, 'Starting unscheduled ladder update')
        return HttpResponseRedirect(reverse('admin:poe_character_changelist'))

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def response_change(self, request, obj):
        if '_update_stats' in request.POST:
            CharacterStatsUpdateTask.delay(  # pylint: disable=no-value-for-parameter
                account_name=obj.profile.poe_profile,
                character_name=obj.name
            )
            messages.add_message(request, messages.INFO, 'Running character update task!')
            return HttpResponseRedirect('.')
        return super().response_change(request, obj)


@admin.register(League)
class PoeLeagueAdmin(admin.ModelAdmin):
    readonly_fields = ('name', 'start_date', 'end_date', 'slug')


@admin.register(Item)
class PoeItemAdmin(admin.ModelAdmin):
    fields = ('name', 'icon', 'preview')
    list_display = ('name', 'small_preview')
    readonly_fields = ('preview', )

    def preview(self, obj: Item):
        if obj and obj.icon:
            return mark_safe(f'<img src="{obj.icon}" style="max-width:600px"/>')

    def small_preview(self, obj: Item):
        return mark_safe(f'<img src="{obj.icon}" style="max-height:20px"/>')
