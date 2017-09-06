Stripe
======

Installation
------------

1. Make sure Lorikeet is installed with the ``stripe`` extra, by running ``pip install https://gitlab.com/abre/lorikeet.git[stripe]``.
2. Add ``'lorikeet.extras.stripe'`` to your ``INSTALLED_APPS``.
3. Set the ``STRIPE_API_KEY`` variable in ``settings.py`` to your Stripe API key.


Usage
-----

.. note::

    These examples use the :doc:`js`, but everything works the same if you're using the :doc:`api` directly, since the JavaScript API is only a thin wrapper.

On creation, the Stripe payment method takes only one parameter, the token that you get from Stripe.js.

.. code:: js

    Stripe.card.createToken(form, function(status, response){
        if (status == 200){
            client.addPaymentMethod("StripeCard", {token: response.id})
        }
    })

Once they're created, in the cart they'll show up with their brand and last 4 digits.

.. code:: js

    console.log(client.cart.payment_methods)
    // [{
    //     type: "StripeCard",
    //     url: "/_cart/payment-methods/1/",
    //     selected: true,
    //     data: {brand: "Visa", last4: "4242"},
    // }]


If you try to charge the card and the charge fails,
