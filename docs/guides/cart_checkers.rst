Preventing Checkout with Completeness and Cart Checkers
=======================================================

**Cart checkers** are functions that determine whether or not a cart can be checked out in its current state. If a cart is ready to be checked out, and all cart checkers pass, it is said to be **complete**.

.. note::

    **Cart checkers** and **completeness** are similar to the concept of **validators** and **validation** in Django and Django REST Framework, but not quite the same. Validators check for cases that are totally invalid; for instance, a delivery address missing a postcode, or a line item where the quantity is a string rather than a number might be invalid. In contrast,cart checkers check for cases that are valid states for the cart to be in, but for which checkout shouldn't be allowed; for instance, when there are no line items, or when a payment method is missing.

Cart checkers are run in two places. One is in the :http:get:`/_cart/` endpoint, where any checkers that fail are listed in ``incomplete_reasons``, so the client user interface can show details. The other is in the :http:post:`/_cart/checkout/` endpoint, where any checkers that fail will prevent checkout from happening, resulting in a **422** response with a reason of ``"incomplete"``.

Writing a Cart Checker
----------------------

Cart checkers are functions that accept a :class:`~lorikeet.models.Cart` instance as an argument; they should either raise a :class:`~lorikeet.exceptions.IncompleteCartError` if the cart is not ready to be checked out, or return successfully if it is.

Here's one that's built in to Lorikeet:

::

    def payment_method_required(cart):
        """Checks that a payment method is set on the cart."""

        if cart.payment_method is None:
            raise IncompleteCartError(code='not_set',
                                      message='A payment method is required.',
                                      field='payment_method')

If your cart checker identifies multiple different reasons the cart can't be checked out, it should instead raise a :class:`~lorikeet.exceptions.IncompleteCartErrorSet`, which can be passed a list of :class:`~lorikeet.exceptions.IncompleteCartError` instances.

Once you've written your cart checker, add it to the :data:`LORIKEET_CART_COMPLETE_CHECKERS` setting.

.. warning::

    The default value for :data:`LORIKEET_CART_COMPLETE_CHECKERS` contains important built-in checkers that you probably don't want to disable, because they prevent things like going through checkout with an empty cart. If you override this setting, make sure you include them!

Checking Individual Line Items and Adjustments
----------------------------------------------

Line items and adjustments both provide a :meth:`~lorikeet.models.LineItem.is_complete` method, which work as the method equivalent of a cart checker; whenever Lorikeet needs to check if a cart is complete, that method is called on every line item and adjustment in the cart, and :class:`~lorikeet.exceptions.IncompleteCartError` exceptions are handled just as described above.

.. note::

    Remember, just like cart checkers, these methods won't prevent a line item or adjustment from being created; they'll only prevent the cart from being checked out.

    Before adding an ``is_complete`` method, consider whether it's more appropriate to use validation in your Django model or Django REST Framework serializer instead.

Built-in Cart Checkers
----------------------

The built-in cart checkers are documented in the :ref:`api-cart-checkers` section of the API documentation.

Handling an Incomplete Cart on the Client
-----------------------------------------

.. todo::

    Document the API side of things
