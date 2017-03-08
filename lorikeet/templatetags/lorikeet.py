from json import dumps

from django import template

from .. import api_serializers

register = template.Library()


@register.simple_tag(takes_context=True)
def lorikeet_cart(context):
    """Returns the current state of the user's cart.

    Returns a JSON string of the same shape as a response from
    :http:get:`/_cart/`. Requires that the current request be in the
    template's context.
    """
    cart = context['request'].get_cart()
    data = api_serializers.CartSerializer(
        cart, context={'request': context['request']}).data
    return dumps(data)
