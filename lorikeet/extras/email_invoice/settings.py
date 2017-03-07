from django.conf import settings

LORIKEET_EMAIL_INVOICE_SUBJECT = getattr(
    settings, 'LORIKEET_EMAIL_INVOICE_SUBJECT',
    "Your order ID {order.invoice_id}")

LORIKEET_EMAIL_INVOICE_FROM_ADDRESS = getattr(
    settings, 'LORIKEET_EMAIL_INVOICE_FROM_ADDRESS',
    "orders@example.com")

LORIKEET_EMAIL_INVOICE_TEMPLATE_HTML = getattr(
    settings, 'LORIKEET_EMAIL_INVOICE_TEMPLATE_HTML', None)

LORIKEET_EMAIL_INVOICE_TEMPLATE_TEXT = getattr(
    settings, 'LORIKEET_EMAIL_INVOICE_TEMPLATE_TEXT', None)
