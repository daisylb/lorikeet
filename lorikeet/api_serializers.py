from rest_framework import serializers, fields
from . import models
from django.core.urlresolvers import reverse
from itertools import chain

class LineItemSerializerRegistry(dict):
    def register(self, model, serializer):
        self[model.__name__] = serializer

    def get_serializer_class(self, instance):
        return self[instance.__class__.__name__]

    def get_serializer(self, instance):
        return self[instance.__class__.__name__](instance)

registry = LineItemSerializerRegistry()


class PrimaryKeyModelSerializer(serializers.ModelSerializer):
    """A serializer that accepts the primary key of an object as input.

    When read from, this serializer works exactly the same as ModelSerializer.
    When written to, it accepts a valid primary key of an existing instance
    of the same model.

    This class is provided as

    This class is part of the public API.
    """
    def get_queryset(self):
        return self.Meta.model.objects.all()

    def to_internal_value(self, repr):
        return self.get_queryset().get(pk=repr)


class RegistryRelatedField(fields.Field):
    def to_representation(self, instance):
        return registry.get_serializer(instance).data


class RegistryRelatedWithMetadataSerializer(serializers.Serializer):
    type = fields.SerializerMethodField()
    data = fields.SerializerMethodField()

    def get_type(self, instance):
        return instance.__class__.__name__

    def get_data(self, instance):
        return RegistryRelatedField().to_representation(instance)


class LineItemMetadataSerializer(RegistryRelatedWithMetadataSerializer):
    total = fields.SerializerMethodField()
    url = fields.SerializerMethodField()

    def get_total(self, instance):
        return str(instance.get_total())

    def get_url(self, instance):
        return reverse('lorikeet:cart-item', kwargs={'id': instance.id})


class DeliveryAddressSerializer(RegistryRelatedWithMetadataSerializer):
    selected = fields.SerializerMethodField()

    def get_selected(self, instance):
        return instance == self.context.get('selected')


class PaymentMethodSerializer(RegistryRelatedWithMetadataSerializer):
    selected = fields.SerializerMethodField()

    def get_selected(self, instance):
        return instance == self.context.get('selected')


class SubclassListSerializer(serializers.ListSerializer):
    def to_representation(self, instance, *args, **kwargs):
        instance = instance.select_subclasses()
        return super().to_representation(instance, *args, **kwargs)


class CartSerializer(serializers.ModelSerializer):
    items = SubclassListSerializer(child=LineItemMetadataSerializer())
    new_item_url = fields.SerializerMethodField()
    delivery_addresses = fields.SerializerMethodField()
    new_address_url = fields.SerializerMethodField()
    payment_methods = fields.SerializerMethodField()
    new_payment_method_url = fields.SerializerMethodField()
    grand_total = fields.DecimalField(max_digits=7, decimal_places=2, source='get_grand_total')

    def get_new_item_url(self, _):
        return reverse('lorikeet:add-to-cart')

    def get_new_address_url(self, _):
        return reverse('lorikeet:new-address')

    def get_delivery_addresses(self, _):
        request = self.context.get('request')
        selected = None
        the_set = []

        if request:
            selected = request.get_cart().delivery_address_subclass

        if request and request.user.is_authenticated():
            the_set = request.user.delivery_addresses.all()

        if selected is not None and selected not in the_set:
            the_set = chain(the_set, [selected])

        return DeliveryAddressSerializer(instance=the_set, many=True, context={'selected': selected}).data

    def get_new_payment_method_url(self, _):
        return reverse('lorikeet:new-payment-method')

    def get_payment_methods(self, cart):
        request = self.context.get('request')
        the_set = []

        selected = cart.payment_method_subclass

        if request and request.user.is_authenticated():
            the_set = request.user.delivery_addresses.all()

        if selected is not None and selected not in the_set:
            the_set = chain(the_set, [selected])

        return PaymentMethodSerializer(instance=the_set, many=True, context={'selected': selected}).data

    class Meta:
        model = models.Cart
        fields = ('items', 'new_item_url', 'delivery_addresses',
                  'new_address_url', 'payment_methods',
                  'new_payment_method_url', 'grand_total')


class LineItemSerializer(serializers.ModelSerializer):
    """Base serializer for LineItem subclasses.

    This is part of the public API.
    """
    def __init__(self, instance=None, *args, **kwargs):
        if 'cart' in kwargs:
            self.cart = kwargs.pop('cart')
        elif instance is not None:
            self.cart =  instance.cart
        else:
            raise TypeError("Either instance or cart arguments must be "
                            "provided to {}".format(self.__class__.__name__))
        return super().__init__(instance, *args, **kwargs)

    def create(self, validated_data):
        validated_data['cart'] = self.cart
        return super().create(validated_data)
