Settings
--------

Lorikeet's behaviour can be altered by setting the following settings in your project's ``settings.py`` file.

.. describe:: LORIKEET_CART_COMPLETE_CHECKERS

    .. todo:: document this

.. describe:: LORIKEET_ORDER_DETAIL_VIEW

    **Default value**: ``None``

    The name of a URL pattern that points to a view describing a single :class:`~lorikeet.models.Order` object. The regex for this URL pattern must have an ``id`` kwarg that matches the numeric ID of the order object; custom invoice IDs in URLs are not yet supported.

    This value should be the same as the string you'd pass as the first argument to ``django.core.urlresolvers.reverse()``, e.g. ``'products:order'``.

    If set, it will be used in :func:`lorikeet.models.Order.get_absolute_url` and :http:post:`/_cart/checkout/`.