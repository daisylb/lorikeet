from decimal import ROUND_DOWN, Decimal
from json import loads

import pytest
from shop import factories, models as smodels


@pytest.mark.django_db
def test_empty_cart(client):
    resp = client.get("/_cart/")
    data = loads(resp.content.decode("utf-8"))
    generated_at = data.pop("generated_at")
    assert isinstance(generated_at, float)
    assert data == {
        "items": [],
        "new_item_url": "/_cart/new/",
        "subtotal": "0.00",
        "delivery_addresses": [],
        "new_address_url": "/_cart/new-address/",
        "payment_methods": [],
        "new_payment_method_url": "/_cart/new-payment-method/",
        "adjustments": [],
        "new_adjustment_url": "/_cart/new-adjustment/",
        "grand_total": "0.00",
        "incomplete_reasons": [
            {
                "code": "not_set",
                "field": "delivery_address",
                "message": "A delivery address is required.",
            },
            {
                "code": "not_set",
                "field": "payment_method",
                "message": "A payment method is required.",
            },
            {
                "code": "empty",
                "field": "items",
                "message": "There are no items in the cart.",
            },
            {
                "code": "not_set",
                "field": "email",
                "message": "An email address is required.",
            },
        ],
        "is_complete": False,
        "checkout_url": "/_cart/checkout/",
        "is_authenticated": False,
        "email": None,
        "compatible_version": 2,
        "incompatible_version": 1,
    }


@pytest.mark.django_db
def test_empty_cart_logged_in(admin_client):
    resp = admin_client.get("/_cart/")
    data = loads(resp.content.decode("utf-8"))
    generated_at = data.pop("generated_at")
    assert isinstance(generated_at, float)
    assert data == {
        "items": [],
        "new_item_url": "/_cart/new/",
        "subtotal": "0.00",
        "delivery_addresses": [],
        "new_address_url": "/_cart/new-address/",
        "payment_methods": [],
        "new_payment_method_url": "/_cart/new-payment-method/",
        "adjustments": [],
        "new_adjustment_url": "/_cart/new-adjustment/",
        "grand_total": "0.00",
        "incomplete_reasons": [
            {
                "code": "not_set",
                "field": "delivery_address",
                "message": "A delivery address is required.",
            },
            {
                "code": "not_set",
                "field": "payment_method",
                "message": "A payment method is required.",
            },
            {
                "code": "empty",
                "field": "items",
                "message": "There are no items in the cart.",
            },
        ],
        "is_complete": False,
        "checkout_url": "/_cart/checkout/",
        "is_authenticated": True,
        "email": None,
        "compatible_version": 2,
        "incompatible_version": 1,
    }


@pytest.mark.django_db
def test_cart_contents(client, cart):
    # set up cart contents
    i = factories.MyLineItemFactory(cart=cart)

    # add some more line items not attached to the cart
    factories.MyLineItemFactory()
    factories.MyLineItemFactory()

    resp = client.get("/_cart/")
    data = loads(resp.content.decode("utf-8"))
    assert data["items"] == [
        {
            "type": "MyLineItem",
            "url": "/_cart/{}/".format(i.id),
            "data": {
                "product": {
                    "id": i.product.id,
                    "name": i.product.name,
                    "unit_price": str(i.product.unit_price),
                },
                "quantity": i.quantity,
            },
            "total": str(i.product.unit_price * i.quantity),
        }
    ]
    assert data["grand_total"] == str(i.product.unit_price * i.quantity)


@pytest.mark.django_db
def test_cart_contents_with_adjustment(client, cart):
    # set up cart contents
    i = factories.MyLineItemFactory(cart=cart)

    # add some more line items not attached to the cart
    factories.MyLineItemFactory()
    factories.MyLineItemFactory()

    # add an adjustment
    a = factories.CartDiscountFactory(cart=cart)

    # add more adjustments not attached to the cart
    factories.CartDiscountFactory()
    factories.CartDiscountFactory()

    resp = client.get("/_cart/")
    data = loads(resp.content.decode("utf-8"))
    discount = (-cart.get_subtotal() * (Decimal(a.percentage) / 100)).quantize(
        Decimal(".01"), rounding=ROUND_DOWN
    )
    assert data["adjustments"] == [
        {
            "type": "CartDiscount",
            "url": "/_cart/adjustment/{}/".format(i.id),
            "data": {"percentage": a.percentage},
            "total": str(discount),
        }
    ]
    assert data["grand_total"] == str((i.product.unit_price * i.quantity) + discount)


@pytest.mark.django_db
def test_cart_delivery_addresses(client, cart):
    # set up cart contents
    cart.delivery_address = factories.AustralianDeliveryAddressFactory()
    cart.save()

    # Add another address not attached to the card
    factories.AustralianDeliveryAddressFactory()

    resp = client.get("/_cart/")
    data = loads(resp.content.decode("utf-8"))
    assert data["delivery_addresses"] == [
        {
            "type": "AustralianDeliveryAddress",
            "selected": True,
            "data": {
                "addressee": cart.delivery_address.addressee,
                "address": cart.delivery_address.address,
                "suburb": cart.delivery_address.suburb,
                "state": cart.delivery_address.state,
                "postcode": cart.delivery_address.postcode,
            },
            "url": "/_cart/address/{}/".format(cart.delivery_address_id),
        }
    ]


@pytest.mark.django_db
def test_cart_delivery_addresses_logged_in(admin_user, admin_client, admin_cart):
    # set up cart contents
    admin_cart.delivery_address = factories.AustralianDeliveryAddressFactory(
        addressee="Active Address", user=admin_user
    )
    admin_cart.save()
    other_addr = factories.AustralianDeliveryAddressFactory(
        user=admin_user, addressee="Inactive Address"
    )

    # Add another address not attached to the card
    factories.AustralianDeliveryAddressFactory()
    factories.AustralianDeliveryAddressFactory(
        user=admin_user, active=False, addressee="Disabled Address"
    )

    resp = admin_client.get("/_cart/")
    data = loads(resp.content.decode("utf-8"))
    assert data["delivery_addresses"] == [
        {
            "type": "AustralianDeliveryAddress",
            "selected": True,
            "data": {
                "addressee": admin_cart.delivery_address.addressee,
                "address": admin_cart.delivery_address.address,
                "suburb": admin_cart.delivery_address.suburb,
                "state": admin_cart.delivery_address.state,
                "postcode": admin_cart.delivery_address.postcode,
            },
            "url": "/_cart/address/{}/".format(admin_cart.delivery_address_id),
        },
        {
            "type": "AustralianDeliveryAddress",
            "selected": False,
            "data": {
                "addressee": other_addr.addressee,
                "address": other_addr.address,
                "suburb": other_addr.suburb,
                "state": other_addr.state,
                "postcode": other_addr.postcode,
            },
            "url": "/_cart/address/{}/".format(other_addr.id),
        },
    ]


@pytest.mark.django_db
def test_cart_payment_methods(client, cart):
    # set up cart contents
    cart.payment_method = smodels.PipeCard.objects.create(card_id="Visa4242")
    cart.save()

    # add a payment method not attached to the card
    smodels.PipeCard.objects.create(card_id="Mastercard4242")

    resp = client.get("/_cart/")
    data = loads(resp.content.decode("utf-8"))
    assert data["payment_methods"] == [
        {
            "type": "PipeCard",
            "selected": True,
            "data": {"brand": "Visa", "last4": "4242"},
            "url": "/_cart/payment-method/{}/".format(cart.payment_method_id),
        }
    ]


@pytest.mark.django_db
def test_cart_payment_methods_logged_in(admin_user, admin_client, admin_cart):
    # set up cart contents
    admin_cart.payment_method = smodels.PipeCard.objects.create(card_id="Visa4242")
    admin_cart.save()
    other = smodels.PipeCard.objects.create(card_id="Discover4242", user=admin_user)

    # add a payment method not attached to the card
    smodels.PipeCard.objects.create(card_id="Mastercard4242")
    smodels.PipeCard.objects.create(card_id="Amex4242", user=admin_user, active=False)

    resp = admin_client.get("/_cart/")
    data = loads(resp.content.decode("utf-8"))
    # we don't care about the order
    assert data["payment_methods"] == [
        {
            "type": "PipeCard",
            "selected": False,
            "data": {"brand": "Discover", "last4": "4242"},
            "url": "/_cart/payment-method/{}/".format(other.id),
        },
        {
            "type": "PipeCard",
            "selected": True,
            "data": {"brand": "Visa", "last4": "4242"},
            "url": "/_cart/payment-method/{}/".format(admin_cart.payment_method_id),
        },
    ]
