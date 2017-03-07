HTTP API
========

.. http:get:: /_cart/

    The current state of the current user's cart. An example response body looks like this:

    .. sourcecode:: javascript

        {
            "items": [/* omitted */],
            "new_item_url": "/_cart/new/",
            "delivery_addresses": [
                
            ],
            "new_address_url": "/_cart/new-address/",
            "payment_methods": [/* omitted */],
            "new_payment_method_url": "/_cart/new-payment-method/",
            "grand_total": "12.00",
            "generated_at": 1488413101.985875,
            "is_complete": false,
            "incomplete_reasons": [
                {
                    "code": "not_set",
                    "field": "payment_method",
                    "message": "A payment method is required."
                }
            ],
            "checkout_url": "/_cart/checkout/",
            "is_authenticated": true,
            "email": null
        }
    
    The meaning of the keys is as follows:

    - ``items`` - The list of items in the cart. Each entry in this list is a JSON blob with the same structure as the :http:get:`/_cart/(id)/` endpoint.
    - ``delivery_addresses`` - The list of all delivery addresses available to the user. Each entry in this list is a JSON blob with the same structure as the :http:get:`/_cart/address/(id)/` endpoint.
    - ``email`` - The email address attached to the cart, as set by :http:patch:`/_cart/`.


.. http:patch:: /_cart/

    Set an email address on this cart. This API call is useful for sites that allow anonymous checkout. Note that you **must** use the ``PATCH`` method, and you cannot update any fields other than ``email``.

    An example request body looks like this:

    .. sourcecode:: javascript

        {"email": "joe.bloggs@example.com"}
    
    The email value can also be ``null`` to un-set the value.

    :statuscode 200: The email was changed successfully.
    :statuscode 400: The supplied email was invalid.


.. http:get:: /_cart/(id)/

    Details about a particular item in the cart. An example response body looks like this:

    .. sourcecode:: javascript

        {
            "type": "WineLineItem",
            "data": {
                "product": {
                    "id": 11,
                    "name": "Moscato 2016",
                    "photo": "/media/moscato.png",
                    "unit_price": "12.00"
                },
                "quantity": 1
            },
            "total": "12.00",
            "url": "/_cart/77/"
        }

.. http:get:: /_cart/address/(id)/

    Details about a particular delivery address that is available for the user. An example response body looks like this:

    .. sourcecode:: javascript

        {
            "type": "AustralianDeliveryAddress",
            "data": {
                "addressee": "Joe Bloggs",
                "address": "123 Fake St",
                "suburb": "Adelaide",
                "state": "SA",
                "postcode": "5000"
            },
            "selected": true,
            "url": "/_cart/address/55/"
        }

.. http:post:: /_cart/checkout/

    Finalise the checkout process; process the payment and generate an order.

    :statuscode 200: Checkout succesful; payment has been processed and order has been generated.
    :statuscode 422: Checkout failed, either because the cart was not ready for checkout or the payment failed.

    This endpoint should be called without any parameters, but the user's cart should be in a state that's ready for checkout; that is the ``is_complete`` key returned in :http:get:`/_cart/` should be ``true``, and ``incomplete_reasons`` should be empty.

    If checkout was successful, the response body will look like this:

    .. sourcecode:: javascript

        {
            "id": 7,
            "url": "/products/order/7/",
        }
    
    where the returned ``id`` is the ID of the :class:`~lorikeet.models.Order` instance that was created, and the ``url`` is a URL generated from the ``LORIKEET_ORDER_DETAIL_VIEW`` setting (or ``null`` if that setting is not set).

    If the cart was not ready for checkout, the endpoint will return a 422 response with a body that looks like this:

    .. sourcecode:: javascript

        {
            "reason": "incomplete",
            "info": [
                {
                    "message": "There are no items in the cart.",
                    "field": "items",
                    "code": "empty"
                }
            ]
        }
    
    In this case, the ``reason`` is always the string ``"incomplete"``, and the ``info`` is the same list of values as in the ``incomplete_reasons`` key returned in :http:get:`/_cart/`.

    If processing the payment failed, the endpoint will return a 422 response with a body that looks like this:

    .. sourcecode:: javascript

        {
            "reason": "payment",
            "payment_method": "StripeCard",
            "info": {
                "message": "Your card was declined.",
                // ...
            }
        }
    
    In this case, the ``reason`` is always the string ``"payment"``; ``payment_method`` is the name of the :class:`~lorikeet.models.PaymentMethod` subclass that handled the payment. ``info`` is data returned by the payment method itself; consult its documentation for its meaning.


.. todo::

    describe the other endpoints

Why does Lorikeet's API work like this?
---------------------------------------

By now, you'll have noticed that Lorikeet's API isn't structured like most REST APIs, with different endpoints returning a bunch of paginated collections of resources you can query from. Instead, there's one endpoint that returns one object containing the entire contents of the API. That resource contains sub-resources which do have their own endpoints, but they're only really useful for making modifications with ``POST``, ``PUT`` and ``PATCH``.

This design is inspired by Facebook's GraphQL, as well as web frontend state management libraries like Redux. In GraphQL, an entire API is conceptually a single object, which can be filtered and have parameters passed to its properties. In Lorikeet, the entire API is *literally* a single object, with no filtering or parameterisation, because the amount of data an individual user cares about is compact and practical to return all at once. The ``POST``, ``PUT`` and ``PATCH`` endpoints, on the other hand, can be thought of as roughly analogous to Redux actions; there's not much to gain by merging these into a single endpoint.
