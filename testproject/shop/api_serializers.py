import codecs

from lorikeet.api_serializers import (LineItemSerializer,
                                      PrimaryKeyModelSerializer)
from rest_framework import fields, serializers

from . import models


class ProductSerializer(PrimaryKeyModelSerializer):

    class Meta:
        model = models.Product
        fields = ('id', 'name', 'unit_price')


class MyLineItemSerializer(LineItemSerializer):
    product = ProductSerializer()

    class Meta:
        model = models.MyLineItem
        fields = ('product', 'quantity',)


class AustralianDeliveryAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.AustralianDeliveryAddress
        fields = ('addressee', 'address', 'suburb', 'state', 'postcode')


class PipeCardSerializer(serializers.ModelSerializer):
    card_token = fields.CharField(max_length=30, write_only=True)
    brand = fields.SerializerMethodField()
    last4 = fields.SerializerMethodField()

    class Meta:
        model = models.PipeCard
        fields = ('card_token', 'brand', 'last4')

    def get_brand(self, object):
        return object.card_id[:-4]

    def get_last4(self, object):
        return object.card_id[-4:]

    def create(self, validated_data):
        card_token = validated_data.pop('card_token')
        validated_data['card_id'] = codecs.encode(card_token, 'rot13')
        return super().create(validated_data)


class CartDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartDiscount
        fields = ('percentage',)
