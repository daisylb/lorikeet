import requests
from django.conf import settings
from django.core.cache import cache
from django.db import models
from lorikeet.models import Order

CACHE_KEY_TPL = "au.com.cmv.open-source.lorikeet.starshipit.order-status.{}"


class StarShipItOrder(models.Model):
    order = models.OneToOneField(Order, related_name="starshipit_order")

    @property
    def status(self):
        """Get the status of this order.

        Returns a dictionary in the format returned by the `StarShipIt
        API <http://support.starshipit.com/hc/en-us/articles/203827019-Tracking>`_.
        Note that the values returned might not match the documentation.

        Values returned from this function are cached for 5 minutes.
        """
        invoice_id = self.order.invoice_id
        cache_key = CACHE_KEY_TPL.format(invoice_id)
        cached_status = cache.get(cache_key)
        if cached_status is not None:
            return cached_status

        status = requests.get('https://api2.starshipit.com/tracking', params={
            'apikey': settings.STARSHIPIT_API_KEY,
            'OrderNumber': self.order.invoice_id,
            'format': 'json',
        }).json()
        cache.set(cache_key, status, 300)
        return status
