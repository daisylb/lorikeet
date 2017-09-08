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

.. autodata:: lorikeet.api_serializers.registry
    :annotation:

    .. automethod:: lorikeet.api_serializers.registry.register

.. autoclass:: lorikeet.api_serializers.PrimaryKeyModelSerializer
    :members:

.. autoclass:: lorikeet.api_serializers.LineItemSerializer
    :members:

Mixins
------

.. autoclass:: lorikeet.mixins.OrderMixin

Template Tags
-------------

.. autofunction:: lorikeet.templatetags.lorikeet.lorikeet_cart

.. _api-cart-checkers:

Cart Checkers
-------------

.. autofunction:: lorikeet.cart_checkers.delivery_address_required

.. autofunction:: lorikeet.cart_checkers.payment_method_required

.. autofunction:: lorikeet.cart_checkers.cart_not_empty

.. autofunction:: lorikeet.cart_checkers.email_address_if_anonymous

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

.. data:: LORIKEET_CART_COMPLETE_CHECKERS

    **Default value**:

    .. code::

        [
            'lorikeet.cart_checkers.delivery_address_required',
            'lorikeet.cart_checkers.payment_method_required',
            'lorikeet.cart_checkers.cart_not_empty',
            'lorikeet.cart_checkers.email_address_if_anonymous',
        ]
    
    Checkers that validate whether or not a cart is ready for checkout. For more detail on these, including how to write your own, refer to the guide on :doc:`/guides/cart_checkers`.

    .. warning::

        The default value for :data:`LORIKEET_CART_COMPLETE_CHECKERS` contains important built-in checkers that you probably don't want to disable, because they prevent things like going through checkout with an empty cart. If you override this setting, make sure you include them!


.. describe:: LORIKEET_ORDER_DETAIL_VIEW

    **Default value**: ``None``

    The name of a URL pattern that points to a view describing a single :class:`~lorikeet.models.Order` object. The regex for this URL pattern must have an ``id`` kwarg that matches the numeric ID of the order object; custom invoice IDs in URLs are not yet supported.

    This value should be the same as the string you'd pass as the first argument to ``django.core.urlresolvers.reverse()``, e.g. ``'products:order'``.

    If set, it will be used in :func:`lorikeet.models.Order.get_absolute_url` and :http:post:`/_cart/checkout/`.

.. describe:: LORIKEET_SET_CSRFTOKEN_EVERYWHERE

    **Default value**: ``True``

    The Lorikeet JavaScript library expects the CSRF token cookie to be set, but it isn't always (see the warning in `the Django CSRF docs <https://docs.djangoproject.com/en/1.10/ref/csrf/#ajax>`_). For convenience, Lorikeet tells Django to set the cookie on every request (the equivalent of calling `ensure_csrf_cookie() <https://docs.djangoproject.com/en/1.10/ref/csrf/#django.views.decorators.csrf.ensure_csrf_cookie>`_ on every request). If you wish to handle this yourself, you can set this setting to ``False`` to disable this behaviour.

.. describe:: LORIKEET_INVOICE_ID_GENERATOR

    **Default value**: ``None``

    .. todo::

        Document this here as well as in recipes


Signals
-------

.. py:data:: lorikeet.signals.order_checked_out

    Fired when a cart is checked out and an order is generated.

    **Parameters**:

    - ``order`` - the :class:`~lorikeet.models.Order` instance that was just created.

    Signal handlers can return a dictionary, which will be merged into the response returned to the client when the checkout happens. They can also return ``None``, but should not return anything else.

    If signals raise an exception, the exception will be logged at the ``warning`` severity level; it's up to you to be able to report this and respond appropriately.

    .. note::

        This signal is fired synchronously during the checkout process, before the checkout success response is returned to the client. If you don't need to return data to the client, try to avoid doing any long-running or failure-prone processes inside handlers for this signal.

        For example, if you need to send order details to a fulfilment provider, you could use a signal handler to enqueue a task in something like `Celery <http://www.celeryproject.org/>`_, or you could have a model with a one-to-one foreign key which you create in a batch process.