from json import dumps, loads

import pytest
from shop import models as smodels

from . import models


@pytest.mark.django_db
def test_checkout(client, filled_cart):
    resp = client.post('/_cart/checkout/', dumps({}),
                       content_type='application/json')
    assert resp.status_code == 200
    assert loads(resp.content.decode('utf-8')) == {
        'success': True,
        'id': 1,
    }
    filled_cart.refresh_from_db()
    assert filled_cart.items.count() == 0
    assert models.Order.objects.count() == 1


@pytest.mark.django_db
def test_cart_incomplete(client, cart):
    resp = client.post('/_cart/checkout/', dumps({}),
                       content_type='application/json')
    assert resp.status_code == 422
    assert loads(resp.content.decode('utf-8')) == {
        'success': False,
        'reason': 'incomplete',
        'info': [
            {
                'code': 'not_set',
                'field': 'delivery_address',
                'message': 'A delivery address is required.',
            },
            {
                'code': 'not_set',
                'field': 'payment_method',
                'message': 'A payment method is required.',
            },
        ],
    }
    assert models.Order.objects.count() == 0


@pytest.mark.django_db
def test_payment_failed(client, filled_cart):
    filled_cart.payment_method = smodels.PipeCard.objects.create(
        card_id="Visa4949")
    filled_cart.save()

    resp = client.post('/_cart/checkout/', dumps({}),
                       content_type='application/json')
    assert resp.status_code == 422
    assert loads(resp.content.decode('utf-8')) == {
        'success': False,
        'reason': 'payment',
        'payment_method': 'PipeCard',
        'info': 'Insufficient funds',
    }
    filled_cart.refresh_from_db()
    assert filled_cart.items.count() == 2
    assert models.Order.objects.count() == 0
