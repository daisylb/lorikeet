from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from . import models


@receiver(user_logged_in)
def merge_carts(sender, user, request, **kwargs):
    # Try to find the session's cart. If there isn't one, we return;
    # there's nothing to merge.
    if 'cart_id' in request.session:
        try:
            session_cart = models.Cart.objects.get(
                id=request.session['cart_id'])
        except models.Cart.DoesNotExist:
            return
    else:
        return

    # Try to find the user's cart.
    try:
        user_cart = models.Cart.objects.get(user=user)
    except models.Cart.DoesNotExist:
        # User doesn't have a cart but the session does, so just assign
        # that one to the user.
        session_cart.user = user
        session_cart.save()
        request._cart = session_cart
    else:
        # Now we have to merge things properly.
        for item in session_cart.items.all():
            # TODO: Some sort of check to see if items can be combined.
            item.cart = user_cart
            item.save()

        if session_cart.delivery_address_id:
            addr = session_cart.delivery_address
            addr.user = user
            addr.save()
            user_cart.delivery_address = addr

        if session_cart.payment_method_id:
            method = session_cart.payment_method
            method.user = user
            method.save()
            user_cart.payment_method = method

        user_cart.save()
        session_cart.delete()
        del request.session['cart_id']
        request._cart = user_cart
