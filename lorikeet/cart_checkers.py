from .exceptions import IncompleteCartError


def delivery_address_required(cart):
    """Prevents checkout unless a delivery address is selected."""

    if cart.delivery_address is None:
        raise IncompleteCartError(
            "not_set", "A delivery address is required.", "delivery_address"
        )


def payment_method_required(cart):
    """Prevents checkout unless a payment method is selected."""

    if cart.payment_method is None:
        raise IncompleteCartError(
            "not_set", "A payment method is required.", "payment_method"
        )


def cart_not_empty(cart):
    """Prevents checkout of an empty cart."""

    if not cart.items.exists():
        raise IncompleteCartError("empty", "There are no items in the cart.", "items")


def email_address_if_anonymous(cart):
    """Prevents anonymous users checking out without an email address."""

    if not cart.user and not cart.email:
        raise IncompleteCartError("not_set", "An email address is required.", "email")
