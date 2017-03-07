Python API
==========

Models
------

.. autoclass:: lorikeet.models.Cart
    :members:

.. autoclass:: lorikeet.models.LineItem
    :members:

.. autoclass:: lorikeet.models.DeliveryAddress
    :members:

.. autoclass:: lorikeet.models.PaymentMethod
    :members:

.. autoclass:: lorikeet.models.Order
    :members:

Serializers
-----------

.. autoclass:: lorikeet.api_serializers.LineItemSerializerRegistry
    :members:

.. autoclass:: lorikeet.api_serializers.PrimaryKeyModelSerializer
    :members:

Mixins
------

.. autoclass:: lorikeet.mixins.OrderMixin

Exceptions
----------

.. autoclass:: lorikeet.exceptions.PaymentError
    :members:

.. autoclass:: lorikeet.exceptions.IncompleteCartError
    :members:

.. autoclass:: lorikeet.exceptions.IncompleteCartErrorSet
    :members:

Settings
--------

Lorikeet's behaviour can be altered by setting the following settings in your project's ``settings.py`` file.

.. describe:: LORIKEET_CART_COMPLETE_CHECKERS

    A list of functions that check to see if a cart is complete and ready to be checked out. Each one takes a :class:`lorikeet.models.Cart` object as its only argument, and raises an :class:`~lorikeet.exceptions.IncompleteCartError` (or potentially a :class:`~lorikeet.exceptions.IncompleteCartErrorSet` containing multiple) if it finds any reasons that the cart should not be checked out.

.. describe:: LORIKEET_ORDER_DETAIL_VIEW

    **Default value**: ``None``

    The name of a URL pattern that points to a view describing a single :class:`~lorikeet.models.Order` object. The regex for this URL pattern must have an ``id`` kwarg that matches the numeric ID of the order object; custom invoice IDs in URLs are not yet supported.

    This value should be the same as the string you'd pass as the first argument to ``django.core.urlresolvers.reverse()``, e.g. ``'products:order'``.

    If set, it will be used in :func:`lorikeet.models.Order.get_absolute_url` and :http:post:`/_cart/checkout/`.
