from logging import getLogger

import stripe
from rest_framework import exceptions, fields, serializers

from . import models

logger = getLogger(__name__)


class StripeAPIException(exceptions.APIException):
    status_code = 422

    def __init__(self, info):
        super().__init__()
        self.detail = {
            'reason': 'stripe',
            'info': info,
        }


class StripeCardSerializer(serializers.ModelSerializer):
    token = fields.CharField(max_length=30, write_only=True)
    brand = fields.SerializerMethodField()
    last4 = fields.SerializerMethodField()

    class Meta:
        model = models.StripeCard
        fields = ('token', 'reusable', 'brand', 'last4')

    def get_brand(self, object):
        return object.data['brand']

    def get_last4(self, object):
        return object.data['last4']

    def create(self, validated_data):
        request = self.context['request']

        if validated_data['reusable']:
            logger.debug("Creating a reusable card record")
            customer = None

            try:
                if request.user.is_authenticated():
                    first_card = models.StripeCard.objects.filter(
                        user=request.user,
                        customer_id__isnull=False,
                    ).order_by('id').first()
                    if first_card is not None:
                        customer = stripe.Customer.retrieve(
                            first_card.customer_id)
                if customer is None:
                    customer = stripe.Customer.create()

                card = customer.sources.create(source=validated_data['token'])
            except stripe.error.CardError as e:
                raise StripeAPIException(e.json_body['error'])

            validated_data['card_id'] = card['id']
            validated_data['customer_id'] = customer['id']
        else:
            validated_data['token_id'] = validated_data['token']
        del validated_data['token']

        return super().create(validated_data)
