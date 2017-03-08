from django.contrib.sessions.middleware import SessionMiddleware

from . import signal_handlers as handlers
from . import models


def with_session(request):
    """Annotate a request object with a session"""
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    return request


def test_merge_carts_both_empty(admin_user, rf):
    request = with_session(rf.post('/'))
    handlers.merge_carts(sender=admin_user.__class__,
                         user=admin_user,
                         request=request)

    assert not models.Cart.objects.count()


def test_merge_carts_user_only(admin_user, admin_cart, rf):
    request = with_session(rf.post('/'))
    handlers.merge_carts(sender=admin_user.__class__,
                         user=admin_user,
                         request=request)

    assert models.Cart.objects.count() == 1


def test_merge_carts_session_only(admin_user, cart, rf):
    request = with_session(rf.post('/'))
    request.session['cart_id'] = cart.id
    handlers.merge_carts(sender=admin_user.__class__,
                         user=admin_user,
                         request=request)

    assert models.Cart.objects.count() == 1
    cart.refresh_from_db()
    assert cart.user == admin_user


def test_merge_empty_carts(admin_user, admin_cart, cart, rf):
    request = with_session(rf.post('/'))
    request.session['cart_id'] = cart.id
    handlers.merge_carts(sender=admin_user.__class__,
                         user=admin_user,
                         request=request)

    assert models.Cart.objects.count() == 1
    admin_cart.refresh_from_db()
    assert admin_cart.id
    assert 'cart_id' not in request.session


def test_merge_filled_carts(admin_user, filled_admin_cart, filled_cart, rf):
    request = with_session(rf.post('/'))
    request.session['cart_id'] = filled_cart.id
    user_cart_item_count = filled_admin_cart.items.count()
    session_cart_item_count = filled_cart.items.count()
    session_address_id = filled_cart.delivery_address_id
    session_payment_id = filled_cart.payment_method_id
    handlers.merge_carts(sender=admin_user.__class__,
                         user=admin_user,
                         request=request)

    assert models.Cart.objects.count() == 1
    filled_admin_cart.refresh_from_db()
    assert filled_admin_cart.id
    assert 'cart_id' not in request.session
    assert filled_admin_cart.items.count() == (user_cart_item_count +
                                               session_cart_item_count)
    assert filled_admin_cart.delivery_address_id == session_address_id
    assert filled_admin_cart.payment_method_id == session_payment_id
