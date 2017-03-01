from json import dumps, loads

import pytest
from shop import models as smodels
from shop import factories


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


@pytest.mark.django_db
def test_add_delivery_address_logged_in(admin_user, admin_client, admin_cart):
    resp = admin_client.post('/_cart/new-address/', dumps({
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
    assert smodels.AustralianDeliveryAddress.objects.first().user == admin_user
    admin_cart.refresh_from_db()
    assert admin_cart.delivery_address is not None


@pytest.mark.django_db
def test_view_delivery_address(client, cart):
    cart.delivery_address = factories.AustralianDeliveryAddressFactory()
    cart.save()

    url = '/_cart/address/{}/'.format(cart.delivery_address_id)
    resp = client.get(url)
    data = loads(resp.content.decode('utf-8'))
    assert data == {
        'type': "AustralianDeliveryAddress",
        'data': {
            'addressee': cart.delivery_address.addressee,
            'address': cart.delivery_address.address,
            'suburb': cart.delivery_address.suburb,
            'state': cart.delivery_address.state,
            'postcode': cart.delivery_address.postcode,
        },
        'selected': True,
        'url': url,
    }


@pytest.mark.django_db
def test_view_owned_unselected_delivery_address(admin_user, admin_client):
    addr = factories.AustralianDeliveryAddressFactory(user=admin_user)

    url = '/_cart/address/{}/'.format(addr.id)
    resp = admin_client.get(url)
    data = loads(resp.content.decode('utf-8'))
    assert data == {
        'type': "AustralianDeliveryAddress",
        'data': {
            'addressee': addr.addressee,
            'address': addr.address,
            'suburb': addr.suburb,
            'state': addr.state,
            'postcode': addr.postcode,
        },
        'selected': False,
        'url': url,
    }


@pytest.mark.django_db
def test_view_unowned_delivery_address(admin_user, client):
    addr = factories.AustralianDeliveryAddressFactory(user=admin_user)

    url = '/_cart/address/{}/'.format(addr.id)
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_view_inactive_delivery_address(admin_user, admin_client):
    addr = factories.AustralianDeliveryAddressFactory(user=admin_user,
                                                      active=False)

    url = '/_cart/address/{}/'.format(addr.id)
    resp = admin_client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_select_delivery_address(admin_user, admin_client, admin_cart):
    addr = factories.AustralianDeliveryAddressFactory(user=admin_user)

    url = '/_cart/address/{}/'.format(addr.id)
    resp = admin_client.patch(url, dumps({'selected': True}),
                              content_type='application/json')
    assert resp.status_code == 200
    admin_cart.refresh_from_db()
    assert admin_cart.delivery_address_id == addr.id


@pytest.mark.django_db
def test_select_inactive_delivery_address(admin_user, admin_client, admin_cart):
    addr = factories.AustralianDeliveryAddressFactory(user=admin_user,
                                                      active=False)

    url = '/_cart/address/{}/'.format(addr.id)
    resp = admin_client.patch(url, dumps({'selected': True}),
                              content_type='application/json')
    assert resp.status_code == 404
    admin_cart.refresh_from_db()
    assert admin_cart.delivery_address_id != addr.id


@pytest.mark.django_db
def test_delete_delivery_address(client, cart):
    addr = factories.AustralianDeliveryAddressFactory()
    cart.delivery_address = addr
    cart.save()

    url = '/_cart/address/{}/'.format(addr.id)
    resp = client.delete(url)
    assert resp.status_code == 204
    cart.refresh_from_db()
    assert cart.delivery_address is None
    addr.refresh_from_db()
    assert not addr.active
