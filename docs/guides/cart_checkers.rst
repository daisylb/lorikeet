Cart Checkers
=============

**Cart checkers** are functions that determine whether or not a cart can be checked out in its current state. If a cart is ready to be checked out, and all cart checkers pass, it is said to be **complete**.

If you think of the entire cart as being like a form, cart checkers are like validators. (We don't actually call them that, because Django REST Framework validators perform a separate function within Lorikeet; ensuring that individual instances of :class:`~lorikeet.models.LineItem`, :class:`~lorikeet.models.DeliveryAddress` and so on are valid.)

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

Built-in Cart Checkers
----------------------

The built-in cart checkers are documented in the :ref:`api-cart-checkers` section of the API documentation.

Handling an Incomplete Cart on the Client
-----------------------------------------

.. todo::

    Document the API side of things