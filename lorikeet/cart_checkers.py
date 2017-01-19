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
