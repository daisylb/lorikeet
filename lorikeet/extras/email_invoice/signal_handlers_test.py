import pytest
from lorikeet import models


@pytest.mark.django_db
def test_checkout(settings, client, filled_cart, mailoutbox):
    settings.INSTALLED_APPS += ['lorikeet.extras.email_invoice']

    client.post('/_cart/checkout/',
                content_type='application/json')

    assert len(mailoutbox) == 1
    order = models.Order.objects.first()
    m = mailoutbox[0]
    assert m.subject == 'Your order ID {}'.format(order.invoice_id)
    assert 'Invoice ID: {}'.format(order.invoice_id) in m.body
    assert m.from_email == 'orders@example.com'
    assert list(m.to) == [order.guest_email]


@pytest.mark.django_db
def test_checkout_copy(settings, client, filled_cart, mailoutbox):
    settings.LORIKEET_EMAIL_INVOICE_COPY_ADDRESS = 'invcopy@example.com'
    if 'lorikeet.extras.email_invoice' not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS += ['lorikeet.extras.email_invoice']

    client.post('/_cart/checkout/',
                content_type='application/json')

    assert len(mailoutbox) == 2
    order = models.Order.objects.first()
    m = mailoutbox[1]
    assert m.subject == 'Your order ID {}'.format(order.invoice_id)
    assert 'Invoice ID: {}'.format(order.invoice_id) in m.body
    assert m.from_email == 'orders@example.com'
    assert list(m.to) == ['invcopy@example.com']
