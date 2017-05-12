import stripe
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from lorikeet.exceptions import PaymentError
from lorikeet.models import Payment, PaymentMethod


class StripeCard(PaymentMethod):
    token_id = models.CharField(max_length=30, blank=True, null=True)
    card_id = models.CharField(max_length=30, blank=True, null=True)
    # We store a customer token per-card rather than per-user, because we might
    # have a user that adds a card, then logs in afterwards, and Stripe doesn't
    # let us move tokens between cards. If the user _is_ logged in when creating
    # the card, though, we try to reuse an existing Stripe customer that belongs
    # to them.
    customer_id = models.CharField(max_length=30, blank=True, null=True)
    reusable = models.BooleanField()

    def clean(self):
        super().clean()
        errors = {}
        if self.reusable:
            if self.token_id is not None:
                errors['token_id'] = ValidationError(
                    "token_id cannot be set if save is true")
            if not self.card_id:
                errors['card_id'] = ValidationError(
                    "card_id must be set if save is true")
            if not self.customer_id:
                errors['customer_id'] = ValidationError(
                    "customer_id must be set if save is true")
        else:
            if not self.token_id:
                errors['token_id'] = ValidationError(
                    "token_id must be set if save is false")
            if self.card_id is not None:
                errors['card_id'] = ValidationError(
                    "card_id cannot be set if save is false")
            if self.customer_id is not None:
                errors['customer_id'] = ValidationError(
                    "customer_id cannot be set if save is false")

        if errors:
            raise ValidationError(errors)

    @property
    def data(self):
        """Returns the corresponding customer object from the Stripe API"""
        cache_key = 'w4yl.apps.stripe:card_data:{}'.format(
            self.card_id or self.token_id)
        card = cache.get(cache_key)
        if card is None:
            if self.reusable:
                customer = stripe.Customer.retrieve(self.customer_id)
                card = customer.sources.retrieve(self.card_id)
            else:
                token = stripe.Token.retrieve(self.token_id)
                card = token['card']
            cache.set(cache_key, card, 3600)
        return card

    def make_payment(self, order, amount):
        if not self.reusable:
            self.active = False
            self.save()
        try:
            chg = stripe.Charge.create(
                amount=int(amount * 100),
                currency='AUD',
                customer=self.customer_id,
                source=self.card_id or self.token_id,
                description='Lorikeet Order {}'.format(order.invoice_id),
                metadata={
                    'is_lorikeet_order': True,
                    'lorikeet_order_id': order.id,
                    'invoice_id': order.invoice_id,
                    'user_id': order.user_id,
                    'email': order.email,
                }
            )
        except stripe.error.CardError as e:
            raise PaymentError(e.json_body['error'])
        else:
            return StripePayment.objects.create(method=self,
                                                charge_id=chg['id'])


class StripePayment(Payment):
    charge_id = models.CharField(max_length=30)
