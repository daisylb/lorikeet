import pytest
from .exceptions import IncompleteCartErrorSet


@pytest.mark.django_db
def test_default_check_succeeds_cart_full(filled_cart):
    result = filled_cart.is_complete()
    assert not filled_cart.errors
    assert result


@pytest.mark.django_db
def test_default_check_fails_cart_empty(cart):
    result = cart.is_complete()
    assert cart.errors
    assert not result
    assert cart.errors.to_json() == [
        {
            'code': 'not_set',
            'field': 'delivery_address',
            'message': 'A delivery address is required.',
        },
        {
            'code': 'not_set',
            'field': 'payment_method',
            'message': 'A payment method is required.',
        },
        {
            'code': 'empty',
            'field': 'items',
            'message': 'There are no items in the cart.',
        },
        {
            'code': 'not_set',
            'field': 'email',
            'message': 'An email address is required.',
        },
    ]


@pytest.mark.django_db
def test_raise_exc(cart):

    with pytest.raises(IncompleteCartErrorSet):
        cart.is_complete(raise_exc=True)
