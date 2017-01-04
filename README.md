# Lorikeet

Lorikeet is a simple, generic, API-only shopping cart framework for Django.

## Design Goals

- **Be customisable, without being overbearing.** Rather than providing an extremely complex application with bells, whistles and configuration options to satisfy every use case, lorikeet provides a shopping cart framework, on top of which you can build your online store. In this regard, Lorikeet is heavily inspired by [Django-SHOP](https://django-shop.readthedocs.io/en/latest/architecture.html).
- **Be minimal.** Lorikeet's sole concern is the shopping cart and checkout process. Lorikeet has no knowledge of things like products, variations, categories, and so on, nor does it contain views to display these things. This is in keeping with the previous design goal, because it allows you to structure both the data model and UI of your products in a way that makes sense for the site you're building.
- **Be loosely coupled.** While Lorikeet was originally built as part of an online store that uses Django CMS and React, it does not depend on either, and could be used with any CMS or frontend framework, or none at all. Lorikeet provides an optional companion set of reusable React components for the checkout experience, but the REST API used to manipulate the cart is well-documented and considered part of the library's public API surface.
- **Get out of the way.** One of the core design goals of the project Lorikeet was extracted from is to provide a simple, low-friction checkout experience. Lorikeet was designed from the ground up to enable this.

## Implementation Guide

### Install Lorikeet

TODO

### Build the Backend

#### Create a LineItem Model

The first thing you'll need to do is define what sort of things can go into your cart, by subclassing the LineItem model. Here's what a simple LineItem model looks like:

```python
from django.db import models
from lorikeet.models import LineItem

class MyLineItem(LineItem):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    quoted_unit_price = models.DecimalField(max_digits=7, decimal_places=2)

    def get_total(self):
        return self.quantity * self.quoted_unit_price
```

A LineItem stores everything the shop needs to know about a single line in a cart or on an invoice. In this simple example, we only store a foreign key to a product and a quantity, but you might want to store more attributes here; for instance, if you're selling T-shirts you might need fields for colour and size, or if you're selling goods by the kilogram you might make `quantity` a `DecimalField`.

LineItems are also used to store invoice history, so they need to be able to calculate the original total cost, even when the rest of the database changes. That's we've added a `quoted_unit_price` field; later we'll use it to store the price of the product at the time it was added to the cart, so that later price changes don't affect existing invoices or carts. (Of course, you might want price changes to affect existing carts; we'll cover this use case later.)

#### Create a LineItem Serializer

Next, you'll need to create a serializer, so you can create new LineItems from your frontend. You should subclass these from `LineItemSerializer`, but otherwise write them as you would a normal Django REST Framework serializer.

In this example, we've done just that, and we've also made a serializer for our

- First, our `quoted_unit_price` is read-only, because we don't want our users to be able to set it themselves, but we do need to set it when a new cart item is created. So, we need to override `create()` on our serializer to set it.
- Second, when we write the frontend later, we want to be able to set the product on a cart item with only its primary key value, but when we retrieve the item from the API

```python
from rest_framework import fields
from lorikeet.api_serializers import (LineItemSerializer,
                                            PrimaryKeyModelSerializer)

from . import models


class ProductSerializer(PrimaryKeyModelSerializer):
    class Meta:
        model = models.Product
        fields = ('id', 'name', 'unit_price')


class WineLineItemSerializer(LineItemSerializer):
    product = ProductSerializer()
    class Meta:
        model = models.WineLineItem
        fields = ('product', 'quantity', 'quoted_unit_price')
        read_only_fields = ('quoted_unit_price',)

    def create(self, validated_data):
        validated_data['quoted_unit_price'] = Decimal('12.34')
        return super().create(validated_data)
```

Your products and line items are now all done. You don't need to write any APIViews or ViewSets or Router entries for your serializers, because Lorikeet provides all of that for you.

### Build the frontend

TODO
