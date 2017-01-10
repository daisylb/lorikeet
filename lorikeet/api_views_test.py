from json import dumps, loads

import pytest
from shop import models as smodels
from shop import factories

from . import models


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
def test_cart_contents(client, cart):
    i = factories.MyLineItemFactory(cart=cart)
    resp = client.get('/_cart/cart/')
    data = loads(resp.content.decode('utf-8'))
    assert data['items'] == [{
        'type': 'MyLineItem',
        'url': '/_cart/cart/{}/'.format(i.id),
        'data': {
            'product': {
                'id': i.product.id,
                'name': i.product.name,
                'unit_price': str(i.product.unit_price),
            },
            'quantity': i.quantity,
        },
        'total': str(i.product.unit_price * i.quantity),
    }]
    assert data['grand_total'] == str(i.product.unit_price * i.quantity)


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
def test_view_cart_item(client, cart):
    i = factories.MyLineItemFactory(cart=cart)
    resp = client.get('/_cart/cart/{}/'.format(i.id))
    data = loads(resp.content.decode('utf-8'))
    assert data == {
        'product': {
            'id': i.product.id,
            'name': i.product.name,
            'unit_price': str(i.product.unit_price),
        },
        'quantity': i.quantity,
    }


@pytest.mark.django_db
def test_cannot_view_cart_item_not_in_cart(client):
    i = factories.MyLineItemFactory()
    resp = client.get('/_cart/cart/{}/'.format(i.id))
    assert resp.status_code == 404
    assert smodels.MyLineItem.objects.count() == 1


@pytest.mark.django_db
def test_remove_cart_item(client, cart):
    i = factories.MyLineItemFactory(cart=cart)
    resp = client.delete('/_cart/cart/{}/'.format(i.id))
    assert resp.status_code == 204
    assert smodels.MyLineItem.objects.count() == 0


@pytest.mark.django_db
def test_cannot_remove_cart_item_not_in_cart(client):
    i = factories.MyLineItemFactory()
    resp = client.delete('/_cart/cart/{}/'.format(i.id))
    assert resp.status_code == 404
    assert smodels.MyLineItem.objects.count() == 1


@pytest.mark.django_db
def test_change_cart_item(client, cart):
    i = factories.MyLineItemFactory(cart=cart)
    resp = client.patch('/_cart/cart/{}/'.format(i.id), dumps({
        'quantity': 3,
    }), content_type='application/json')
    assert resp.status_code == 200
    assert smodels.MyLineItem.objects.get(id=i.id).quantity == 3


@pytest.mark.django_db
def test_add_delivery_address(client, cart):
    resp = client.post('/_cart/cart/new-address/', dumps({
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


@pytest.mark.django_db
def test_add_payment_method(client, cart):
    resp = client.post('/_cart/cart/new-payment-method/', dumps({
        'type': "PipeCard",
        'data': {
            'card_token': 'Lvfn4242',
        },
    }), content_type='application/json')
    assert resp.status_code == 201
    assert smodels.PipeCard.objects.count() == 1
    cart.refresh_from_db()
    assert cart.payment_method is not None
