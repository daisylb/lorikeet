from django.apps import AppConfig


class EmailInvoiceAppConfig(AppConfig):
    name = 'lorikeet.extras.email_invoice'

    def ready(self):
        from . import signal_handlers  # noqa
