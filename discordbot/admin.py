from django.contrib import admin
from .models import Wisdom, DiscordUser, Gachi

class WisdomAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'text')
    list_filter = ('date',)
    search_fields = ('text',)
    fields = ('author', 'text')

class DiscordUserAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'id')
    search_fields = ('display_name',)

admin.site.register(Wisdom, WisdomAdmin)
admin.site.register(DiscordUser, DiscordUserAdmin)
admin.site.register(Gachi)