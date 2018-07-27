from logging import getLogger

from django.core.mail import send_mail
from django.dispatch import receiver
from django.template.loader import render_to_string
from lorikeet.signals import order_checked_out
from premailer import transform

from . import textify
from .settings import settings

logger = getLogger(__name__)


@receiver(order_checked_out)
def send_email_invoice(sender, order, request, **kwargs):
    subject = settings.subject.format(order=order)
    recipient = order.user.email if order.user else order.guest_email

    if recipient is None:
        return {'invoice_email': None}

    ctx = {
        'order': order,
        'order_url': request.build_absolute_uri(order.get_absolute_url(token=True)),
    }
    mail_kwargs = {}
    if settings.template_html:
        html = render_to_string(settings.template_html, ctx)
        html = transform(html, base_url=request.build_absolute_uri())
        mail_kwargs['html_message'] = html

    if settings.template_text:
        text = render_to_string(settings.template_text, ctx)
        mail_kwargs['message'] = text
    elif settings.template_html:
        mail_kwargs['message'] = textify.transform(html)
    else:
        raise ValueError("No HTML or text template set")

    logger.debug('Sending an invoice email to %s', recipient)
    send_mail(
        subject=subject,
        from_email=settings.from_address,
        recipient_list=[recipient],
        **mail_kwargs
    )
    if settings.copy_address:
        send_mail(
            subject=subject,
            from_email=settings.from_address,
            recipient_list=[settings.copy_address],
            **mail_kwargs
        )

    return {'invoice_email': recipient}
