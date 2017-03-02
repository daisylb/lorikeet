JavaScript API
==============

Lorikeet comes with a small JavaScript library to make manipulating the cart from client JavaScript a little easier. It provides convenience creation, update and delete methods for line items, delivery addresses and payment methods, and also keeps the state of the shopping cart in sync if it's open in multiple tabs using ``localStorage``.

It supports IE11, the latest versions of Safari, Edge and Firefox, and the two latest versions of Chrome. It requires a ``window.fetch`` polyfill for IE and Safari.

Installation
------------

The JavaScript component of Lorikeet can be installed via NPM (to be used with a bundler like Webpack). In the future, it will also be provided as a CDN-hosted file you can reference in a ``<script>`` tag. To install it, run ``npm install https://gitlab.com/abre/lorikeet``.

Usage
-----

If you're using the NPM version, ``import CartClient from 'lorikeet'`` or ``var CartClient = require('lorikeet')`` as appropriate for your setup.

Use the CartClient constructor to instantiate the client. This is the object you'll use to interact with the API.

.. code:: javascript

    var client = new CartClient('/_cart/')

You can now access the current state of the cart on ``client.cart``, which exposes the entire contents of the main endpoint of the :doc:`api`.

.. code:: javascript

    console.log(client.cart.grand_total) // "123.45"
    console.log(client.cart.items.length) // 3

You can listen for changes using the ``addListener`` and ``removeListener`` events.

.. code:: javascript

    var listenerRef = client.addListener(function(cart){console.log("Cart updated", cart)})
    client.removeListener(listenerRef)

All of the members of the lists at ``client.cart.items``, ``client.cart.delivery_addresses`` and ``client.cart.payment_methods`` have a ``delete()`` method. Members of ``client.cart.items`` also have ``update(data)`` method, which performs a partial update (``PATCH`` request) using the data you pass, and members of the other two have a ``select()`` method that, makes them the active delivery address or payment method.

.. code:: javascript

    client.cart.items[0].update({quantity: 3})
    client.cart.items[1].delete()
    client.cart.delivery_addresses[2].select()
    client.cart.payment_methods[3].delete()

There's also ``addItem``, ``addAddress`` and ``addPaymentMethod`` methods, which take a type of line item, address or payment method as their first item, and a blob in the format expected by the corresponding serializer as the second.

.. code:: javascript

    client.addItem("MyLineItem", {product: 1, quantity: 2})
    client.addAddress("AustralianDeliveryAddress", {
      addressee: "Adam Brenecki",
      address: "Commercial Motor Vehicles Pty Ltd\nLevel 1, 290 Wright St",
      suburb: "Adelaide", state: "SA", postcode: "5000",
    })
    client.addPaymentMethod("PipeCard", {card_token: "tok_zdchtodladvrcmkxsgvq"})

Reference
---------

.. js:autoclass:: CartClient

    .. js:autofunction:: CartClient#addItem
    .. js:autofunction:: CartClient#addAddress
    .. js:autofunction:: CartClient#addPaymentMethod
    .. js:autofunction:: CartClient#addListener
    .. js:autofunction:: CartClient#removeListener

.. js:autoclass:: CartItem

    .. js:autofunction:: CartItem#update

.. js:autoclass:: AddressOrPayment

    .. js:autofunction:: AddressOrPayment#select


Promise Behaviour
-----------------

All of the methods that modify the cart (:js:func:`CartClient.addItem`, :js:func:`CartClient.addAddress`, :js:func:`CartClient.addPaymentMethod`, :js:func:`CartItem.update`, and :js:func:`AddressOrPayment.select`) return Promises, which have the following behaviour.

If the request **succeeds**, the promise will *resolve* with the JSON-decoded representation of the response returned by the relevant API endpoint.

If the request **fails with a network error**, the promise will *reject* with an object that has the following shape:

.. code:: javascript

    {
        reason: 'network',
        error: TypeError("Failed to fetch"), // error from fetch() call
    }

If the request is made, but **receives an error response from the server**, the promise will *reject* with an object that has the following shape:

.. code:: javascript

    {
        reason: 'api',
        status: 422,
        statusText: 'Unprocessable Entity',
        body: "{\"suburb\":[\"This field is…", // Raw response body
        data: {
            suburb: ["This field is required."],
            // ...
        }, // JSON-decoded response body
    }

If an error response is returned from the server, and **the response is not valid JSON**, such as a 500 response with ``DEBUG=True`` or a 502 from a reverse proxy, the promise will instead *reject* with an object that has the following shape:

.. code:: javascript

    {
        reason: 'api',
        status: 502,
        statusText: 'Bad Gateway',
        body: "<html><body><h1>Bad Gateway…", // Raw response body
        decodeError: SyntaxError("Unexpected token < in JSON at position 0"),
    }

React
-----

Lorikeet also comes with optional support for React. To use it, wrap your React app's outermost component in ``CartProvider``, providing your Lorikeet client instance as the ``client`` prop.

.. code:: javascript

    import { CartProvider } from 'lorikeet/react'

    class App extends Component {
      render() {
        return <CartProvider client={myClient}>
            // ...
        </CartProvider>
      }
    }

Then, in any component where you want to use the client, decorate it with ``cartify``, and you'll have access to the client as ``props.cartClient``, as well as a shortcut to the cart itself on ``props.cart``.

.. code:: javascript

    import cartify from 'lorikeet/react'

    class MyCart extends Component {
      handleAddItem(item){
        this.props.cartClient.addItem('ItemType', item)
      }
      render(){
        return <div>My cart has {this.props.cart.items.length} items!</div>
      }
    }

    MyCart = cartify(MyCart)
