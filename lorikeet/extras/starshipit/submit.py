import requests
from django.conf import settings
from lorikeet import models as lorikeet_models

from . import models


def submit_orders():
    orders = lorikeet_models.Order.objects.filter(starshipit_order=None)
    if not orders:
        return
    blob = get_orders_blob(orders)
    requests.post('https://api2.starshipit.com/orders?format=json',
                  json=blob).raise_for_status()
    for order in orders:
        models.StarShipItOrder.objects.create(order=order)


def get_orders_blob(orders):
    return {
        'ApiKey': settings.STARSHIPIT_API_KEY,
        'OrdersList': [get_order_blob(x) for x in orders],
    }


def get_order_blob(order):
    destination = starshipit_repr(order.delivery_address_subclass)
    if 'Email' not in destination:
        destination['Email'] = order.email
    return {
        'OrderNumber': order.invoice_id,
        'Destination': destination,
        'Items': [starshipit_repr(x) for x in order.items.select_subclasses()],
    }


def starshipit_repr(thing):
    if hasattr(thing, 'starshipit_repr'):
        return thing.starshipit_repr()
    klass = thing.__class__.__name__
    if hasattr(settings, 'STARSHIPIT_REPR') and klass in settings.STARSHIPIT_REPR:
        return settings.STARSHIPIT_REPR[klass](thing)
    raise TypeError("Could not serialize %r for StarShipIT", thing)
