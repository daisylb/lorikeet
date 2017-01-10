import factory
from factory.django import DjangoModelFactory

from . import models

class ProductFactory(DjangoModelFactory):
    name = factory.fuzzy.FuzzyText()
    unit_price = factory.fuzzy.FuzzyDecimal()

    class Meta:
        model = models.Product


class MyLineItemFactory(DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)
    quantity = factory.fuzzy.FuzzyInteger()

    class Meta:
        model = models.MyLineItem
