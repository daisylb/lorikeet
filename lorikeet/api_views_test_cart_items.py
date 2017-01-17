from json import dumps, loads

import pytest
from shop import models as smodels
from shop import factories


@pytest.mark.django_db
def test_add_item_to_cart(client):
    p = factories.ProductFactory()
    resp = client.post('/_cart/new/', dumps({
        'type': "MyLineItem",
        'data': {'product': p.id, 'quantity': 2},
    }), content_type='application/json')
    assert resp.status_code == 201
    assert smodels.MyLineItem.objects.count() == 1


@pytest.mark.django_db
def test_view_cart_item(client, cart):
    i = factories.MyLineItemFactory(cart=cart)
    resp = client.get('/_cart/{}/'.format(i.id))
    data = loads(resp.content.decode('utf-8'))
    assert data == {
        'type': "MyLineItem",
        'data': {
            'product': {
                'id': i.product.id,
                'name': i.product.name,
                'unit_price': str(i.product.unit_price),
            },
            'quantity': i.quantity,
        },
        'total': str(i.quantity * i.product.unit_price),
        'url': '/_cart/{}/'.format(i.id),
    }


@pytest.mark.django_db
def test_cannot_view_cart_item_not_in_cart(client):
    i = factories.MyLineItemFactory()
    resp = client.get('/_cart/{}/'.format(i.id))
    assert resp.status_code == 404
    assert smodels.MyLineItem.objects.count() == 1


@pytest.mark.django_db
def test_remove_cart_item(client, cart):
    i = factories.MyLineItemFactory(cart=cart)
    resp = client.delete('/_cart/{}/'.format(i.id))
    assert resp.status_code == 204
    assert smodels.MyLineItem.objects.count() == 0


@pytest.mark.django_db
def test_cannot_remove_cart_item_not_in_cart(client):
    i = factories.MyLineItemFactory()
    resp = client.delete('/_cart/{}/'.format(i.id))
    assert resp.status_code == 404
    assert smodels.MyLineItem.objects.count() == 1


@pytest.mark.django_db
def test_change_cart_item(client, cart):
    i = factories.MyLineItemFactory(cart=cart)
    new_qty = i.quantity + 1
    resp = client.patch('/_cart/{}/'.format(i.id), dumps({
        'data': {'quantity': new_qty},
    }), content_type='application/json')
    print(resp.content)
    assert resp.status_code == 200
    assert smodels.MyLineItem.objects.get(id=i.id).quantity == new_qty
