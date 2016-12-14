# w4yl.apps.cart

This package implements the generic components of the shopping cart functionality of w4yl.

## Design Goals

- **Be customisable, without being overbearing.** Rather than providing an extremely complex application with bells, whistles and configuration options to satisfy every use case, w4yl.apps.cart provides a shopping cart framework, on top of which you can build your online store. In this regard, w4yl.apps.cart is heavily inspired by [Django-SHOP](https://django-shop.readthedocs.io/en/latest/architecture.html).
- **Be minimal.** w4yl.apps.cart's sole concern is the shopping cart and checkout process. w4yl.apps.cart has no knowledge of things like products, variations, categories, and so on, nor does it contain views to display these things. This is in keeping with the previous design goal, because it allows you to structure both the data model and UI of your products in a way that makes sense for the site you're building.
- **Be loosely coupled.** While w4yl.apps.cart was originally built as part of an online store that uses Django CMS and React, it does not depend on either, and could be used with any CMS or frontend framework, or none at all. w4yl.apps.cart provides an optional companion set of reusable React components for the checkout experience, but the REST API used to manipulate the cart is well-documented and considered part of the library's public API surface.
- **Get out of the way.** One of the core design goals of the project w4yl.apps.cart was extracted from is to provide a simple, low-friction checkout experience. w4yl.apps.cart was designed from the ground up to enable this.

## Implementation Guide

### Create a LineItem Model

The first thing you'll need to do is define what sort of things can go into your cart, by subclassing the LineItem model. Here's what a simple LineItem model looks like:

```python
from django.db import models
from w4yl.apps.cart.models import LineItem

class MyLineItem(LineItem):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    quoted_unit_price = models.DecimalField(max_digits=7, decimal_places=2)

    def get_total(self):
        return self.quantity * self.quoted_unit_price
```

A LineItem stores everything the shop needs to know about a single line in a cart or on an invoice. In this simple example, we only store a foreign key to a product and a quantity, but you might want to store more attributes here; for instance, if you're selling T-shirts you might need fields for colour and size, or if you're selling goods by the kilogram you might make `quantity` a `DecimalField`.

LineItems are also used to store invoice history, so they need to be able to calculate the original total cost, even when the rest of the database changes. That's we've added a `quoted_unit_price` field; later we'll use it to store the price of the product at the time it was added to the cart, so that later price changes don't affect existing invoices or carts. (Of course, you might want price changes to affect existing carts; this is also possible, and we'll cover it below.)
