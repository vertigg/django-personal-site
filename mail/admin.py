from django.contrib import admin
from mail.models import Mailbox, EmailMessage

admin.site.register(Mailbox)
admin.site.register(EmailMessage)
