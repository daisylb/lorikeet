import factory
from factory.django import DjangoModelFactory
from factory import fuzzy

from . import models

class ProductFactory(DjangoModelFactory):
    name = fuzzy.FuzzyText()
    unit_price = fuzzy.FuzzyDecimal(1, 200)

    class Meta:
        model = models.Product


class MyLineItemFactory(DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)
    quantity = fuzzy.FuzzyInteger(1, 10)

    class Meta:
        model = models.MyLineItem
