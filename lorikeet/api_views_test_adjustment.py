from json import dumps, loads

import pytest
from shop import factories as sfactories, models as smodels


@pytest.mark.django_db
def test_add_adjustment(client, cart):
    resp = client.post(
        "/_cart/new-adjustment/",
        dumps({"type": "CartDiscount", "data": {"percentage": 25}}),
        content_type="application/json",
    )
    assert resp.status_code == 201
    assert smodels.CartDiscount.objects.count() == 1
    assert cart.adjustments.count() == 1


@pytest.mark.django_db
def test_view_adjustment(client, cart):
    a = sfactories.CartDiscountFactory(cart=cart)

    url = "/_cart/adjustment/{}/".format(a.id)
    resp = client.get(url)
    data = loads(resp.content.decode("utf-8"))
    assert data == {
        "type": "CartDiscount",
        "data": {"percentage": a.percentage},
        "total": "0.00",
        "url": "/_cart/adjustment/{}/".format(a.id),
    }


@pytest.mark.django_db
def test_view_unowned_adjustment(other_cart, client):
    a = sfactories.CartDiscountFactory(cart=other_cart)

    url = "/_cart/adjustment/{}/".format(a.id)
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_delete_adjustment(client, cart):
    a = sfactories.CartDiscountFactory(cart=cart)

    url = "/_cart/adjustment/{}/".format(a.id)
    resp = client.delete(url)
    assert resp.status_code == 204
    with pytest.raises(smodels.CartDiscount.DoesNotExist):
        a.refresh_from_db()


@pytest.mark.django_db
def test_delete_unowned_adjustment(client, other_cart):
    a = sfactories.CartDiscountFactory(cart=other_cart)

    url = "/_cart/adjustment/{}/".format(a.id)
    resp = client.delete(url)
    assert resp.status_code == 404
    a.refresh_from_db()
