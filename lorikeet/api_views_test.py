from json import loads, dumps
from shop import factories, models as smodels
from . import models

import pytest

@pytest.fixture
def cart(client):
    cart = models.Cart.objects.create()
    session = client.session
    session['cart_id'] = cart.id
    session.save()
    return cart

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


@pytest.mark.django_db
def test_empty_cart_logged_in(admin_client):
    resp = admin_client.get('/_cart/cart/')
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


@pytest.mark.django_db
def test_add_item_to_cart(client):
    p = factories.ProductFactory()
    resp = client.post('/_cart/cart/new/', dumps({
        'type': "MyLineItem",
        'data': {'product': p.id, 'quantity': 2},
    }), content_type='application/json')
    assert resp.status_code == 201
    assert smodels.MyLineItem.objects.count() == 1


@pytest.mark.django_db
def test_remove_cart_item(client, cart):
    i = factories.MyLineItemFactory(cart=cart)
    resp = client.delete('/_cart/cart/{}/'.format(i.id))
    assert resp.status_code == 204
    assert smodels.MyLineItem.objects.count() == 0


@pytest.mark.django_db
def test_change_cart_item(client, cart):
    i = factories.MyLineItemFactory(cart=cart)
    resp = client.patch('/_cart/cart/{}/'.format(i.id), dumps({
        'quantity': 3,
    }), content_type='application/json')
    assert resp.status_code == 200
    assert smodels.MyLineItem.objects.get(id=i.id).quantity == 3
