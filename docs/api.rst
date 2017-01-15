HTTP API
========

.. note::

    The HTTP API doesn't *quite* work as described in this document just yet. (It's close, though, and it will soon.) It's documentation-driven development in action!

Lorikeet's API has one primary endpoint, mounted wherever you mounted the Lorikeet app in your URL structure (usually ``/_cart/``). If you send a ``GET`` request to it, you'll get back a JSON blob containing the current state of the end user's cart, which might look something like this:

.. todo::

    Replace with a non-empty example


.. code:: json

    {
        "items": [],
        "new_item_url": "/_cart/new/",
        "delivery_addresses": [],
        "new_address_url": "/_cart/new-address/",
        "payment_methods": [],
        "new_payment_method_url": "/_cart/new-payment-method/",
        "grand_total": "0.00",
    }

.. todo::

    describe the other endpoints

Why does Lorikeet's API work like this?
---------------------------------------

By now, you'll have noticed that Lorikeet's API isn't structured like most REST APIs, with a bunch of paginated collections of resources you can query from. Instead, there's one endpoint that returns one object containing the entire contents of the API. That resource contains sub-resources which do have their own endpoints,

This design is inspired by web frontend state management libraries like Redux, with the ``/_cart/`` endpoint (which only responds to ``GET``) roughly corresponding to the state object, and ``POST`` and ``PUT`` requests to the other endpoints roughly corresponding to
