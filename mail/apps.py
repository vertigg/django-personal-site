from django.apps import AppConfig


class MailConfig(AppConfig):
    name = 'mail'

    def ready(self) -> None:
        from mail.signals import handle_inbound_email
