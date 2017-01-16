import pytest

from . import models


@pytest.fixture
def cart(client):
    cart = models.Cart.objects.create()
    session = client.session
    session['cart_id'] = cart.id
    session.save()
    return cart


@pytest.fixture
def admin_cart(admin_user):
    cart = models.Cart.objects.create(user=admin_user)
    return cart
