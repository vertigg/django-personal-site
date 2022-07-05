from django.conf import settings
from django.db import models


class Mailbox(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=32, unique=True)

    class Meta:
        verbose_name_plural = 'Mailboxes'

    @property
    def email_address(self) -> str:
        return f'{self.name}@{settings.EMAIL_DOMAIN}'

    def __str__(self) -> str:
        return self.email_address


class EmailMessage(models.Model):
    mailbox = models.ForeignKey(Mailbox, on_delete=models.CASCADE)
    subject = models.CharField(max_length=256)
    text = models.TextField()
    html = models.TextField()

    def __str__(self) -> str:
        return f'{self.mailbox} {self.subject}'
