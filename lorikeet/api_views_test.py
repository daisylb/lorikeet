from json import loads

import pytest

@pytest.mark.django_db
def test_empty_cart(client):
    resp = client.get('/_cart/cart/')
    data = loads(resp.content.decode('utf-8'))
    assert data == {
        'items': [],
        'new_item_url': '/_cart/cart/new/',
        'delivery_addresses': [],
        'new_address_url': '/_cart/cart/new-address/',
        'payment_methods': [],
        'new_payment_method_url': '/_cart/cart/new-payment-method/',
        'grand_total': '0.00',
    }
