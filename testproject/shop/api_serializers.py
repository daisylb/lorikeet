from lorikeet.api_serializers import (LineItemSerializer,
                                      PrimaryKeyModelSerializer)

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
