from logging import getLogger

from django.core.mail import send_mail
from django.dispatch import receiver
from django.template.loader import render_to_string
from lorikeet.signals import order_checked_out
from premailer import transform

from . import settings

logger = getLogger(__name__)


@receiver(order_checked_out)
def send_email_invoice(sender, order, request, **kwargs):
    subject = settings.LORIKEET_EMAIL_INVOICE_SUBJECT.format(order=order)
    recipient = order.user.email if order.user else order.guest_email

    if recipient is None:
        return {'invoice_email': None}

    ctx = {
        'order': order,
        'order_url': request.build_absolute_uri(order.get_absolute_url(token=True)),
    }
    html = None
    text = None
    if settings.LORIKEET_EMAIL_INVOICE_TEMPLATE_HTML:
        html = render_to_string(settings.LORIKEET_EMAIL_INVOICE_TEMPLATE_HTML,
                                ctx)
        html = transform(html, base_url=request.build_absolute_uri())
    if settings.LORIKEET_EMAIL_INVOICE_TEMPLATE_TEXT:
        text = render_to_string(settings.LORIKEET_EMAIL_INVOICE_TEMPLATE_TEXT,
                                ctx)

    logger.debug('Sending an invoice email to %s', recipient)
    send_mail(
        subject=subject,
        message=text,
        from_email=settings.LORIKEET_EMAIL_INVOICE_FROM_ADDRESS,
        recipient_list=[recipient],
        html_message=html,
    )

    return {'invoice_email': recipient}
