import pytest
from faker import Faker
from shop import models as smodels
from shop import factories

from . import models


def fill_cart(cart):
    factories.MyLineItemFactory(cart=cart)
    factories.MyLineItemFactory(cart=cart)
    cart.delivery_address = factories.AustralianDeliveryAddressFactory()
    cart.payment_method = smodels.PipeCard.objects.create(card_id="Visa4242")
    if not cart.user:
        cart.email = Faker().safe_email()
    cart.save()


@pytest.fixture
def cart(client):
    cart = models.Cart.objects.create()
    session = client.session
    session['cart_id'] = cart.id
    session.save()
    return cart


@pytest.fixture
def filled_cart(cart):
    fill_cart(cart)
    return cart


@pytest.fixture
def admin_cart(admin_user):
    cart = models.Cart.objects.create(user=admin_user)
    return cart


@pytest.fixture
def filled_admin_cart(admin_cart):
    fill_cart(admin_cart)
    return admin_cart
