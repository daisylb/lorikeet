from django.db import models
from lorikeet.models import LineItem


class Product(models.Model):
    name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=7, decimal_places=2)


class MyLineItem(LineItem):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()

    def get_total(self):
        return self.quantity * self.product.unit_price
