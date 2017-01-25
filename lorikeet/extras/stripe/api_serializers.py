import stripe
from rest_framework import fields, serializers

from . import models


class StripeCardSerializer(serializers.ModelSerializer):
    card_token = fields.CharField(max_length=30, write_only=True)
    brand = fields.SerializerMethodField()
    last4 = fields.SerializerMethodField()

    class Meta:
        model = models.StripeCard
        fields = ('card_token', 'brand', 'last4')

    def get_brand(self, object):
        return object.data['brand']

    def get_last4(self, object):
        return object.data['last4']

    def create(self, validated_data):
        print(self.context)
        request = self.context['request']
        customer = None

        if request.user.is_authenticated():
            first_card = models.StripeCard.objects.filter(
                user=request.user).order_by('id').first()
            if first_card is not None:
                customer = stripe.Customer.retrieve(first_card.customer_token)
        if customer is None:
            customer = stripe.Customer.create()

        card = customer.sources.create(source=validated_data['card_token'])
        validated_data['card_token'] = card['id']
        validated_data['customer_token'] = customer['id']
        return super().create(validated_data)
