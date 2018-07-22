from decimal import ROUND_DOWN, Decimal

from django.db import models
from lorikeet.exceptions import PaymentError
from lorikeet.models import (Adjustment, DeliveryAddress, LineItem, Payment,
                             PaymentMethod)

AUSTRALIAN_STATES = (
    ('NSW', 'New South Wales'),
    ('VIC', 'Victoria'),
    ('QLD', 'Queensland'),
    ('WA', 'Western Australia'),
    ('SA', 'South Australia'),
    ('TAS', 'Tasmania'),
    ('ACT', 'Australian Capital Territory'),
    ('NT', 'Northern Territory'),
)


class Product(models.Model):
    name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=7, decimal_places=2)


class MyLineItem(LineItem):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()

    def get_total(self):
        return self.quantity * self.product.unit_price


class AustralianDeliveryAddress(DeliveryAddress):
    addressee = models.CharField(max_length=255)
    address = models.TextField()
    suburb = models.CharField(max_length=255)
    state = models.CharField(max_length=3, choices=AUSTRALIAN_STATES)
    postcode = models.CharField(max_length=4)


class PipeCard(PaymentMethod):
    card_id = models.CharField(max_length=30)

    def make_payment(self, order, amount):
        if self.card_id.endswith('9'):
            raise PaymentError("Insufficient funds")
        return PipePayment.objects.create(method=self, amount=amount)


class PipePayment(Payment):
    amount = models.DecimalField(max_digits=7, decimal_places=2)


class CartDiscount(Adjustment):
    percentage = models.PositiveSmallIntegerField()

    def get_total(self, subtotal):
        assert isinstance(subtotal, Decimal)
        discount = -subtotal * self.percentage / 100
        return discount.quantize(Decimal('.01'), rounding=ROUND_DOWN)
