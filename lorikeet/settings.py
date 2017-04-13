from django.conf import settings
from django.core.signing import Signer

LORIKEET_CART_COMPLETE_CHECKERS = getattr(
    settings, 'LORIKEET_CART_COMPLETE_CHECKERS', [
        'lorikeet.cart_checkers.delivery_address_required',
        'lorikeet.cart_checkers.payment_method_required',
        'lorikeet.cart_checkers.cart_not_empty',
        'lorikeet.cart_checkers.email_address_if_anonymous',
    ]
)

LORIKEET_ORDER_DETAIL_VIEW = getattr(
    settings, 'LORIKEET_ORDER_DETAIL_VIEW', None
)

LORIKEET_SET_CSRFTOKEN_EVERYWHERE = getattr(
    settings, 'LORIKEET_SET_CSRFTOKEN_EVERYWHERE', True
)

LORIKEET_INVOICE_ID_GENERATOR = getattr(
    settings, 'LORIKEET_INVOICE_ID_GENERATOR', None
)

order_url_signer = Signer(
    salt='au.com.cmv.open-source.lorikeet.order-url-signer')
