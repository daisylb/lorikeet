from django.dispatch import Signal

order_checked_out = Signal(providing_args=['order', 'request'])
