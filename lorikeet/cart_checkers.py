from .exceptions import IncompleteCartError


def delivery_address_required(cart):
    """Checks that a delivery address is set on the cart."""

    if cart.delivery_address is None:
        raise IncompleteCartError('not_set',
                                  'A delivery address is required.',
                                  'delivery_address')


def payment_method_required(cart):
    """Checks that a payment method is set on the cart."""

    if cart.payment_method is None:
        raise IncompleteCartError('not_set',
                                  'A payment method is required.',
                                  'payment_method')


def cart_not_empty(cart):
    """Checks that a payment method is set on the cart."""

    if not cart.items.exists():
        raise IncompleteCartError('empty',
                                  'There are no items in the cart.',
                                  'items')


def email_address_if_anonymous(cart):
    """Checks an email address is set if the user isn't logged in."""

    if not cart.user and not cart.email:
        raise IncompleteCartError('not_set',
                                  'An email address is required.',
                                  'email')
