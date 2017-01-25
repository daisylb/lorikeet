from django.conf import settings

LORIKEET_CART_COMPLETE_CHECKERS = getattr(
    settings, 'LORIKEET_CART_COMPLETE_CHECKERS', [
        'lorikeet.cart_checkers.delivery_address_required',
        'lorikeet.cart_checkers.payment_method_required',
        'lorikeet.cart_checkers.cart_not_empty',
    ]
)
