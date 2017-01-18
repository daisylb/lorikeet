from datetime import date
from json import dumps

import pytest
import stripe
from django.conf import settings

from . import models

pytestmark = pytest.mark.skipif(
    not settings.STRIPE_API_KEY or
    not settings.STRIPE_API_KEY.startswith('sk_test_'),
    reason="A Stripe test API key is required to run tests")


@pytest.fixture
def card_id():
    return stripe.Token.create(card={
        'number': '4242424242424242',
        'exp_month': 12,
        'exp_year': date.today().year + 1,
        'cvc': '123',
    })['id']


@pytest.fixture
def card_obj(card_id):
    customer = stripe.Customer.create()
    card = customer.sources.create(source=card_id)
    return models.StripeCard.objects.create(customer_token=customer['id'],
                                            card_token=card['id'])


@pytest.mark.django_db
def test_add_stripe_card(client, cart, card_id):
    resp = client.post('/_cart/new-payment-method/', dumps({
        'type': "StripeCard",
        'data': {
            'card_token': card_id,
        },
    }), content_type='application/json')
    assert resp.status_code == 201
    assert models.StripeCard.objects.count() == 1
    card_obj = models.StripeCard.objects.first()
    assert card_obj.data['last4'] == '4242'
    assert card_obj.data['brand'] == "Visa"


@pytest.mark.django_db
def test_checkout_with_stripe(client, filled_cart, card_obj):
    filled_cart.payment_method = card_obj
    filled_cart.save()
    resp = client.post('/_cart/checkout/', dumps({}),
                       content_type='application/json')
    assert resp.status_code == 200
    assert models.StripePayment.objects.count() == 1
