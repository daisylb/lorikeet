from json import dumps

import pytest

from . import models


@pytest.mark.django_db
def test_checkout(client, filled_cart):
    print(filled_cart.delivery_address)
    resp = client.post('/_cart/checkout/', dumps({}),
                       content_type='application/json')
    assert resp.status_code == 200
    filled_cart.refresh_from_db()
    assert filled_cart.items.count() == 0
    assert models.Order.objects.count() == 1
