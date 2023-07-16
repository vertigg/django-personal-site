import io
import json
import os
import zipfile
from time import time

from django.conf import settings
from django.contrib import admin, messages
from django.db import models
from django.forms import Textarea, TextInput
from django.http import HttpResponse, HttpResponseRedirect
from django.template.defaultfilters import truncatechars
from django.urls import path
from django.utils.html import mark_safe

from discordbot.models import (
    DiscordLink, DiscordSettings, DiscordUser, MarkovText, MixImage, Wisdom
)
from discordbot.serializers import MixImageSerializer


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


@admin.register(DiscordLink)
class DiscordLinkAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
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
    fields = ('display_name', 'id', 'poe_profile', 'admin', 'mod_group',
              'user')

    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': 20})},
        models.CharField: {'widget': TextInput(attrs={'size': 20})},
    }


@admin.register(MixImage)
class DiscordMixImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'pid', 'checksum', 'date', 'author', 'deleted', 'small_preview')
    readonly_fields = ('checksum', 'date', 'preview')

    def get_urls(self):
        return [path('download/', self.download_backup)] + super().get_urls()

    def preview(self, obj: MixImage):
        return mark_safe(f'<img src="{obj.image.url}" style="max-width:600px"/>')

    def small_preview(self, obj: MixImage):
        return mark_safe(f'<img src="{obj.image.url}" style="max-height:20px"/>')

    small_preview.short_description = 'preview'

    def download_backup(self, request):
        """
        Generates zip archive with all MixImage objects and JSON file with all
        MixImage data from database
        """
        queryset = self.model.objects.all()
        images = [os.path.join(settings.MEDIA_ROOT, x) for x in
                  queryset.values_list('image', flat=True)]
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, 'w') as zip_file:
            # Zip pictures
            for fpath in images:
                _, fname = os.path.split(fpath)
                zip_path = os.path.join('images', fname)
                zip_file.write(fpath, zip_path)

            # Zip database data as json file
            queryset = self.model.objects.all()
            serializer = MixImageSerializer(queryset, many=True)
            zip_file.writestr('data.json', json.dumps(serializer.data, indent=4))

        resp = HttpResponse(buffer.getvalue(), content_type="application/x-zip-compressed")
        resp['Content-Disposition'] = f'attachment; filename=mix_{int(time())}.zip'
        return resp
