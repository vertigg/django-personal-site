from django.contrib import admin
from mail.models import Mailbox, EmailMessage

admin.site.register(Mailbox)


@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_filter = ('mailbox', )
    search_fields = ('subject', )

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]
