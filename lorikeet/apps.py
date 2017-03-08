from django.apps import AppConfig


class LorikeetAppConfig(AppConfig):
    name = 'lorikeet'
    verbose_name = 'Lorikeet'

    def ready(self):
        from . import signal_handlers  # noqa
