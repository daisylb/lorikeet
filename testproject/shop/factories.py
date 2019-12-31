import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

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


class AustralianDeliveryAddressFactory(DjangoModelFactory):
    addressee = factory.Faker("name", locale="en_AU")
    address = factory.Faker("street_address", locale="en_AU")
    suburb = factory.Faker("city", locale="en_AU")
    state = factory.Faker("state_abbr", locale="en_AU")
    postcode = factory.Faker("postcode", locale="en_AU")

    class Meta:
        model = models.AustralianDeliveryAddress


class CartDiscountFactory(DjangoModelFactory):
    percentage = fuzzy.FuzzyInteger(1, 99)

    class Meta:
        model = models.CartDiscount
