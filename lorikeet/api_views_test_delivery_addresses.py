from json import dumps

import pytest
from shop import models as smodels


@pytest.mark.django_db
def test_add_delivery_address(client, cart):
    resp = client.post('/_cart/new-address/', dumps({
        'type': "AustralianDeliveryAddress",
        'data': {
            'addressee': 'Adam Brenecki',
            'address': 'Commercial Motor Vehicles Pty Ltd\n'
                       'Level 1, 290 Wright Street',
            'suburb': 'Adelaide',
            'state': 'SA',
            'postcode': '5000',
        },
    }), content_type='application/json')
    assert resp.status_code == 201
    assert smodels.AustralianDeliveryAddress.objects.count() == 1
    cart.refresh_from_db()
    assert cart.delivery_address is not None
