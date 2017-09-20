The Registry
============

Lorikeet's :doc:`line_items`, Delivery Addresses and Payment Methods are all made up of two components: a model and a serializer. In order to use them, Lorikeet needs to know about each serializer that's available, and which model each one corresponds to.

There's various ways that Lorikeet could associate the two automatically, but they're all failure-prone and difficult to debug. Instead, Lorikeet exposes a registry at :data:`lorikeet.api_serializers.registry` for you to declare those mappings manually.

Mappings can be declared by calling :meth:`lorikeet.api_serializers.registry.register`. You can do this anywhere as long as it gets run when Django starts up, but the best place to do it is the ``ready()`` method of an ``AppConfig`` for your app:

.. code-block:: python

    from django.apps import AppConfig

    class MyAppConfig(AppConfig):
        # ...

        def ready(self):
            from . import models, api_serializers
            from lorikeet.api_serializers import registry

            registry.register(models.MyLineItem,
                              api_serializers.MyLineItemSerializer)
            registry.register(models.MyDeliveryAddress,
                              api_serializers.MyDeliveryAddressSerializer)
            registry.register(models.MyPaymentMethod,
                              api_serializers.MyPaymentMethodSerializer)

.. warning::

    If you're newly setting up an app config for use with Lorikeet, make sure
    Django actually loads it!

    You can do this by either changing your app's entry in `INSTALLED_APPS` to
    the dotted path to your AppConfig (e.g. ``myapp.apps.MyAppConfig``), or
    by adding a line like ``default_app_config = "myapp.apps.MyAppConfig"`` in
    your app's ``__init__.py``.

    For more on app configs, check out the `Django documentation <https://docs.djangoproject.com/en/1.10/ref/applications/#application-configuration>`_.
