from django.conf import settings

LORIKEET_CART_COMPLETE_CHECKERS = getattr(settings, 'CART_VALIDATORS', [
    'lorikeet.cart_checkers.delivery_address_required',
    'lorikeet.cart_checkers.payment_method_required',
])
