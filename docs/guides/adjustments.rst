Adjustments, Discounts and Coupons
==================================

In Lorikeet, anything that changes the total of the cart is an *adjustment*; adjustments are how you'll implement things like discounts and coupon codes.

Adjustments work just the same as line items; they have a model which subclasses :class:`~lorikeet.models.Adjustment`, a serialiser, and the two are associated with each other in the registry.

You just need to override the :meth:`~lorikeet.models.Adjustment.get_total` method; it's passed the subtotal before adjustments are applied, and it should return an amount that is added to the total. (In the case of discounts, this amount should be negative.)

.. note::

    If you're doing any division, and you don't want to deal with fractional cents, your code in :meth:`~lorikeet.models.Adjustment.get_total` is responsible for rounding.

.. code-block:: python
    :caption: models.py

    from django.db import models
    from lorikeet.models import Adjustment

    class Coupon(models.Model):
        code = models.CharField(max_length=128, unique=True)
        valid_from = models.DateTimeField()
        valid_to = models.DateTimeField()
        percentage = models.PositiveSmallIntegerField()

    class CouponAdjustment(Adjustment):
        coupon = models.ForeignKey(CouponCode)

        def get_total(self, subtotal):
            discount = -subtotal * self.percentage / 100
            # Rounding down (towards negative infinity) rounds in favour of
            # the customer
            return discount.quantize(Decimal('.01'), rounding=ROUND_DOWN)


.. todo::

    Write example serializer etc
