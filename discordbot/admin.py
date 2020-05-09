import io
import os
import tempfile
import zipfile
from datetime import datetime

import pandas as pd
from django.conf import settings
from django.contrib import admin, messages
from django.db import models
from django.forms import Textarea, TextInput
from django.http import HttpResponse, HttpResponseRedirect
from django.template.defaultfilters import truncatechars
from django.urls import path

from discordbot.models import (CoronaReport, Counter, CounterGroup,
                               DiscordLink, DiscordSettings, DiscordUser,
                               Gachi, MarkovText, MixImage, WFAlert, Wisdom)


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
            obj.last_update = None
            obj.save()
            messages.add_message(request, messages.INFO, 'Object has been cleared')
            return HttpResponseRedirect('.')
        if '_download' in request.POST:
            buffer = io.StringIO()
            buffer.write(obj.text)
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename={obj.key}.txt'
            return response
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


@admin.register(MixImage)
class DiscordMixImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'pid', 'checksum', 'date', 'author')
    readonly_fields = ('checksum', 'date')

    def get_urls(self):
        return [path('download/', self.download_backup)] + super().get_urls()

    def download_backup(self, request):
        """
        Generates zip archive with all MixImage pictures and CSV file with all
        MixImage data from database 
        """
        date = datetime.now().strftime('%y%m%d%H%M%S')
        file_list = [os.path.join(settings.MEDIA_ROOT, x) for x in
                     self.model.objects.all().values_list('image', flat=True)]
        buffer = io.BytesIO()
        temp_folder = 'mix_pictures'
        zip_filename = f"{temp_folder}_{date}.zip"
        zf = zipfile.ZipFile(buffer, 'w')
        # Zip pictures
        for fpath in file_list:
            _, fname = os.path.split(fpath)
            zip_path = os.path.join(temp_folder, fname)
            zf.write(fpath, zip_path)
        # Zip database data as csv file
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            qs = self.model.objects.all().values()
            df = pd.DataFrame.from_dict(qs)
            filename = f'{temp.name}.csv'
            df.to_csv(filename, index=False)
            zip_path = os.path.join(temp_folder, filename)
            zf.write(filename, zip_path)
        zf.close()
        resp = HttpResponse(buffer.getvalue(), content_type="application/x-zip-compressed")
        resp['Content-Disposition'] = f'attachment; filename={zip_filename}'
        return resp


admin.site.register(WFAlert)
admin.site.register(CoronaReport)
