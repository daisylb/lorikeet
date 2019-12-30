StarShipIT
==========

.. deprecated:: 0.1.5

        Projects that wish to continue using this integration should vendor the ``lorikeet.extras.starshipit`` package within their own projects; it will be removed from Lorikeet before version 1.0 is released.

This integration posts orders to `StarShipIT <http://www.starshipit.com/>`_, a cloud-based fulfilment software provider.

Installation
------------

1. Make sure Lorikeet is installed with the ``starshipit`` extra, by running ``pip install https://github.com/excitedleigh/lorikeet.git[starshipit]``.
2. Add ``'lorikeet.extras.starshipit'`` to your ``INSTALLED_APPS``.
3. Set the ``STARSHIPIT_API_KEY`` variable in ``settings.py`` to your `StarShipIT API key <https://app.shipit.click/Members/Settings/API.aspx>`_.
4. Configure your site to call ``lorikeet.extras.starshipit.submit.submit_orders()`` periodically (using e.g. a management command, django-cron or Celery Beat). If you're using Celery, there's a task at ``lorikeet.extras.starshipit.tasks.submit_orders`` that you can add to your ``CELERYBEAT_SCHEDULE``.

Serialisation
-------------

To work with StarShipIT, all of your cart item and delivery address models should implement a ``.starshipit_repr()`` method. These methods should return a dictionary with keys expected by StarShipIT's `Create Order API endpoint <http://support.starshipit.com/hc/en-us/articles/212209703-Create-Orders>`_: the **ShipmentItem** parameters for a cart item, and **DestinationDetails** for a delivery address.

If you can't do this (for instance, you have cart items or delivery addresses provided by a third-party package), create a ``STARSHIPIT_REPR`` setting in your ``settings.py``. This setting should be a dictionary where the keys are cart item or delivery address model names, and the values are functions that take an instance of that model and return the appropriate value.
