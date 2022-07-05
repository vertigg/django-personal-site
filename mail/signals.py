from anymail.signals import inbound
from django.dispatch import receiver

from mail.models import EmailMessage, Mailbox


@receiver(inbound)
def handle_inbound_email(sender, event, esp_name, **kwargs):
    message = event.message
    recipients = message.envelope_recipient.split(',')

    for recipient in recipients:
        name = recipient.split('@')[0]

        mailbox = Mailbox.objects.filter(name=name).first()
        if not mailbox:
            mailbox, _ = Mailbox.objects.get_or_create(name='unsorted')

        EmailMessage.objects.create(
            text=message.text,
            html=message.html,
            subject=message.subject,
            mailbox=mailbox
        )
