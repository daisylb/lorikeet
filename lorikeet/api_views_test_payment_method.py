from json import dumps, loads

import pytest
from shop import models as smodels


@pytest.mark.django_db
def test_add_payment_method(client, cart):
    resp = client.post('/_cart/new-payment-method/', dumps({
        'type': "PipeCard",
        'data': {
            'card_token': 'Lvfn4242',
        },
    }), content_type='application/json')
    assert resp.status_code == 201
    assert smodels.PipeCard.objects.count() == 1
    cart.refresh_from_db()
    assert cart.payment_method is not None


@pytest.mark.django_db
def test_add_payment_method_logged_in(admin_user, admin_client, admin_cart):
    resp = admin_client.post('/_cart/new-payment-method/', dumps({
        'type': "PipeCard",
        'data': {
            'card_token': 'Lvfn4242',
        },
    }), content_type='application/json')
    assert resp.status_code == 201
    assert smodels.PipeCard.objects.count() == 1
    assert smodels.PipeCard.objects.first().user == admin_user
    admin_cart.refresh_from_db()
    assert admin_cart.payment_method is not None


@pytest.mark.django_db
def test_view_payment_method(client, cart):
    cart.payment_method = smodels.PipeCard.objects.create(card_id='Visa4242')
    cart.save()

    url = '/_cart/payment-method/{}/'.format(cart.payment_method_id)
    resp = client.get(url)
    data = loads(resp.content.decode('utf-8'))
    assert data == {
        'type': 'PipeCard',
        'selected': True,
        'data': {
            'brand': 'Visa',
            'last4': '4242',
        },
        'url': url,
    }


@pytest.mark.django_db
def test_view_owned_unselected_payment_method(admin_user, admin_client):
    pm = smodels.PipeCard.objects.create(card_id='Visa4242', user=admin_user)

    url = '/_cart/payment-method/{}/'.format(pm.id)
    resp = admin_client.get(url)
    data = loads(resp.content.decode('utf-8'))
    assert data == {
        'type': 'PipeCard',
        'selected': False,
        'data': {
            'brand': 'Visa',
            'last4': '4242',
        },
        'url': url,
    }


@pytest.mark.django_db
def test_view_unowned_payment_method(admin_user, client):
    pm = smodels.PipeCard.objects.create(card_id='Visa4242', user=admin_user)

    url = '/_cart/payment-method/{}/'.format(pm.id)
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_view_inactive_payment_method(admin_user, admin_client):
    pm = smodels.PipeCard.objects.create(card_id='Visa4242', user=admin_user,
                                         active=False)

    url = '/_cart/payment-method/{}/'.format(pm.id)
    resp = admin_client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_select_payment_method(admin_user, admin_client, admin_cart):
    pm = smodels.PipeCard.objects.create(card_id='Visa4242', user=admin_user)

    url = '/_cart/payment-method/{}/'.format(pm.id)
    resp = admin_client.patch(url, dumps({'selected': True}),
                              content_type='application/json')
    assert resp.status_code == 200
    admin_cart.refresh_from_db()
    assert admin_cart.payment_method_id == pm.id


@pytest.mark.django_db
def test_select_inactive_payment_method(admin_user, admin_client, admin_cart):
    pm = smodels.PipeCard.objects.create(card_id='Visa4242', user=admin_user,
                                         active=False)

    url = '/_cart/payment-method/{}/'.format(pm.id)
    resp = admin_client.patch(url, dumps({'selected': True}),
                              content_type='application/json')
    assert resp.status_code == 404
    admin_cart.refresh_from_db()
    assert admin_cart.payment_method_id != pm.id


@pytest.mark.django_db
def test_delete_payment_method(client, cart):
    pm = smodels.PipeCard.objects.create(card_id='Visa4242')
    cart.payment_method = pm
    cart.save()

    url = '/_cart/payment-method/{}/'.format(cart.payment_method_id)
    resp = client.delete(url)
    assert resp.status_code == 204
    cart.refresh_from_db()
    assert cart.payment_method is None
    pm.refresh_from_db()
    assert not pm.active
