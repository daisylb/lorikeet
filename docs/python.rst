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

``LORIKEET_CART_COMPLETE_CHECKERS``
...................................

A list of functions that check to see if a cart is complete and ready to be checked out. Each one takes a :class:`lorikeet.models.Cart` object as its only argument, and raises an :class:`~lorikeet.exceptions.IncompleteCartError` (or potentially a :class:`~lorikeet.exceptions.IncompleteCartErrorSet` containing multiple) if it finds any reasons that the cart should not be checked out.
