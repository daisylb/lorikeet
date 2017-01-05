Getting Started Guide
=====================

Install Lorikeet
~~~~~~~~~~~~~~~~

.. todo::

    Add installation instructions

Build the Backend
~~~~~~~~~~~~~~~~~

Create a LineItem Model
^^^^^^^^^^^^^^^^^^^^^^^

The first thing you'll need to do is define what sort of things can go
into your cart, by subclassing the LineItem model. Here's what a simple
LineItem model looks like.

.. code:: python

    from django.db import models
    from lorikeet.models import LineItem

    class MyLineItem(LineItem):
        product = models.ForeignKey(Product, on_delete=models.PROTECT)
        quantity = models.PositiveSmallIntegerField()

        def get_total(self):
            return self.quantity * self.product.unit_price

A LineItem stores everything the shop needs to know about a single line
in a cart or on an invoice. In this simple example, we only store a
foreign key to a product and a quantity, but you might want to store
more attributes here; for instance, if you're selling T-shirts you might
need fields for colour and size, or if you're selling goods by the
kilogram you might make ``quantity`` a ``DecimalField``.

Create a LineItem Serializer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Next, you'll need to create a serializer, so you can create new
LineItems from your frontend. You should subclass these from
``LineItemSerializer``, but otherwise write them as you would a normal
Django REST Framework serializer.

In this example, we've done just that, and we've also made a serializer
for our

-  First, our ``quoted_unit_price`` is read-only, because we don't want
   our users to be able to set it themselves, but we do need to set it
   when a new cart item is created. So, we need to override ``create()``
   on our serializer to set it.
-  Second, when we write the frontend later, we want to be able to set
   the product on a cart item with only its primary key value, but when
   we retrieve the item from the API

.. code:: python

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

Your products and line items are now all done. You don't need to write
any APIViews or ViewSets or Router entries for your serializers, because
Lorikeet provides all of that for you.

Build the frontend
~~~~~~~~~~~~~~~~~~

.. todo::

    Document how the API and JS library work
