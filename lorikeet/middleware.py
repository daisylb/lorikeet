from django.middleware.csrf import get_token

from .models import Cart
from .settings import LORIKEET_SET_CSRFTOKEN_EVERYWHERE


def cart_getter_factory(request):
    def get_cart():
        if hasattr(request, '_cart'):
            return request._cart

        cart = None

        if request.user.is_authenticated():
            cart, _ = Cart.objects.get_or_create(user=request.user)
        elif 'cart_id' in request.session:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                pass

        if cart is None:
            # user is definitely not logged in, might be a new user with no cart,
            # or might be a user with a stale cart that got deleted
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id

        # save the cart on the request over the top of this function,
        # so we don't have to look it up again
        request._cart = cart
        assert bool(cart.user) == request.user.is_authenticated()
        return cart
    return get_cart


class CartMiddleware:

    def process_request(self, request):
        request.get_cart = cart_getter_factory(request)
        if LORIKEET_SET_CSRFTOKEN_EVERYWHERE:
            get_token(request)  # Forces setting the CSRF cookie
