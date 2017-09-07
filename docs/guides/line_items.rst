Line Items
==========

In Lorikeet, a user's shopping cart is made up of one or more line items, each of which models a particular thing in the cart. Each different kind of line item needs to have two things: a model to define what can be stored in it, and a serializer so that your frontend can do the actual storing.

Building a Line Item Model
--------------------------

You might remember from the :doc:`backend tutorial </tutorial/backend>` that line items are subclasses of :class:`lorikeet.models.LineItem`, with a ``get_total`` method that returns how much they cost. That's really all there is to it! Here's the model we made in the tutorial:

.. code:: python

    from django.db import models
    from lorikeet.models import LineItem

    class MyLineItem(LineItem):
        product = models.ForeignKey(Product, on_delete=models.PROTECT)
        quantity = models.PositiveSmallIntegerField()

        def get_total(self):
            return self.quantity * self.product.unit_price

It's worth reiterating that the only two things Lorikeet cares about are the fact that it's a :class:`lorikeet.models.LineItem` subclass, and the fact that it defines a ``get_total`` method. All these other things:

- The details of what's in your ``Product`` model,
- Whether you have a single ``Product`` model, two or more different models (``TShirt`` and ``Mug``, maybe?), or no product model at all,
- What fields are on your ``LineItem`` subclass, or what their types are (for instance, if you're selling T-shirts you might need fields for colour and size, or if you're selling goods by the kilogram you might make ``quantity`` a ``DecimalField``),

Lorikeet doesn't care about those, and you can structure them how you like.

Lorikeet also **isn't limited to one type of line item**. If you sell multiple different kinds of products, like in the ``TShirt`` and ``Mug`` example before, you might need to store different kinds of data on their respective line items; mugs don't come in different sizes and cuts, after all. Lorikeet will let you define a ``TShirtLineItem`` and a ``MugLineItem``, and your users can add a combination of both into their cart.

Building a Line Item Serializer
-------------------------------

You might also remember from the :doc:`backend tutorial </tutorial/backend>` that every line item serializer is a subclass of :class:`lorikeet.api_serializers.LineItemSerializer`. Lorikeet will use this serializer both to populate new line items, and to render existing ones into JSON.

.. code:: python

    from rest_framework import fields
    from lorikeet.api_serializers import (LineItemSerializer,
                                          PrimaryKeyModelSerializer)

    from . import models


    class ProductSerializer(PrimaryKeyModelSerializer):
        class Meta:
            model = models.Product
            fields = ('id', 'name', 'unit_price')


    class MyLineItemSerializer(LineItemSerializer):
        product = ProductSerializer()
        class Meta:
            model = models.MyLineItem
            fields = ('product', 'quantity',)

.. tip::
    If you have any application logic you need to run when you add an item to the cart, you can do it inside the ``create()`` method on the line item's serializer.

Linking it all together
-----------------------

Once you've written your model and serializer, link them together in :doc:`registry`.