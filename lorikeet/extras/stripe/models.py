import stripe
from django.core.cache import cache
from django.db import models
from lorikeet.exceptions import PaymentError
from lorikeet.models import Payment, PaymentMethod


class StripeCard(PaymentMethod):
    card_token = models.CharField(max_length=30)
    # We store a customer token per-card rather than per-user, because we might
    # have a user that adds a card, then logs in afterwards, and Stripe doesn't
    # let us move tokens between cards. If the user _is_ logged in when creating
    # the card, though, we try to reuse an existing Stripe customer that belongs
    # to them.
    customer_token = models.CharField(max_length=30)

    @property
    def data(self):
        """Returns the corresponding customer object from the Stripe API"""
        cache_key = 'w4yl.apps.stripe:card_data:{}'.format(self.id)
        cache_val = cache.get(cache_key)
        if cache_val is not None:
            return cache_val

        customer = stripe.Customer.retrieve(self.customer_token)
        card = customer.sources.retrieve(self.card_token)
        cache.set(cache_key, card, 3600)
        return card

    def make_payment(self, amount):
        try:
            chg = stripe.Charge.create(
                amount=int(amount * 100),
                currency='AUD',
                customer=self.customer_token,
                source=self.card_token,
            )
        except stripe.error.CardError as e:
            raise PaymentError(e.json_body['error'])
        else:
            return StripePayment.objects.create(method=self,
                                                charge_id=chg['id'])


class StripePayment(Payment):
    charge_id = models.CharField(max_length=30)
