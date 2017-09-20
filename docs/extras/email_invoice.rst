Email Invoicing
===============

Installation
------------

1. Make sure Lorikeet is installed with the ``email_invoice`` extra, by running ``pip install https://gitlab.com/abre/lorikeet.git[email_invoice]``.
2. Add ``'lorikeet.extras.email_invoice'`` to your ``INSTALLED_APPS``.
3. Set the ``LORIKEET_EMAIL_INVOICE_SUBJECT`` variable in ``settings.py`` to a subject line.
3. Set the ``LORIKEET_EMAIL_INVOICE_TEMPLATE_HTML`` variable in ``settings.py`` to a HTML template.
4. Set the ``LORIKEET_EMAIL_INVOICE_TEMPLATE_TEXT`` variable in ``settings.py`` to a plain text template.
3. Set the ``LORIKEET_EMAIL_INVOICE_FROM_ADDRESS`` variable in ``settings.py`` to an email address.


Usage
-----

Set the ``LORIKEET_EMAIL_INVOICE_SUBJECT`` setting to the subject line you want your emails to have. You can use the `Python new-style format string syntax <https://docs.python.org/3/library/string.html#format-string-syntax>`_ to reference the :class:`~lorikeet.models.Order` object, e.g. ``"Your invoice for order {order.invoice_id}"``.

Create a HTML template at the path you set ``LORIKEET_EMAIL_INVOICE_TEMPLATE_HTML`` to. It will recieve the :class:`~lorikeet.models.Order` instance in its context as ``order``, and ``order_url`` will be set to the absolute URL to your order details view,

The template will be run through `premailer <https://pypi.python.org/pypi/premailer>`_, so you can safely use ``<style>`` and ``<link rel="stylesheet">`` tags. Of course, you can still only use CSS properties supported by the email clients you're targeting.

.. code-block:: htmldjango


    <html><body>
    <p><a href="{{ order_url }}">To find out the current status of your order, click here.</a></p>
    <h1>Tax Invoice</h1>
    <p>ACME Corporation Pty Ltd<br />ABN 84 007 874 142</p>

    <h2>Invoice {{ order.invoice_id }}</h2>

    <h3>Shipped To</h3>
    {{ order.delivery_address_subclass }}

    <h3>Order Details</h3>
    <table>
        <tr>
            <th>Product</th>
            <th>Quantity</th>
            <th>Subtotal</th>
        </tr>
        {% for item in order.items.select_subclasses %}
            <tr>
                <td>{{ item.product.name }}</td>
                <td>{{ item.quantity }}</td>
                <td>{{ item.total }}</td>
            </tr>
        {% endfor %}
        <tr>
        <tr>
            <td colspan='2'>Total</td>
            <td>{{ order.grand_total }}</td>
        </tr>
    </table>
    </body></html>

Then, create a plain-text template at the path you set ``LORIKEET_EMAIL_INVOICE_TEMPLATE_TEXT`` to. It will recieve the same context.
