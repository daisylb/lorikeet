from itertools import chain
from time import time

from django.core.urlresolvers import reverse
from rest_framework import fields, serializers

from . import models


class LineItemSerializerRegistry:
    """Registers serializers with their associated models.

    This is used instead of discovery or a metaclass-based registry as
    making sure the classes to be registered actually get imported can be
    fragile and non-obvious to debug.

    The registry instance is available at
    ``lorikeet.api_serializers.registry``.
    """

    def __init__(self):
        self.line_items = {}
        self.payment_methods = {}
        self.delivery_addresses = {}

    def register(self, model, serializer):
        """Associate ``model`` with ``serializer``."""
        print(model.__mro__)
        if issubclass(model, models.LineItem):
            self.line_items[model.__name__] = serializer
        elif issubclass(model, models.PaymentMethod):
            self.payment_methods[model.__name__] = serializer
        elif issubclass(model, models.DeliveryAddress):
            self.delivery_addresses[model.__name__] = serializer
        else:
            raise ValueError("model must be a subclass of "
                             "LineItem, PaymentMethod or DeliveryAddress")

    def get_serializer_class(self, instance):
        if isinstance(instance, models.LineItem):
            return self.line_items[instance.__class__.__name__]
        if isinstance(instance, models.PaymentMethod):
            return self.payment_methods[instance.__class__.__name__]
        if isinstance(instance, models.DeliveryAddress):
            return self.delivery_addresses[instance.__class__.__name__]
        raise ValueError("instance must be an instance of a "
                         "LineItem, PaymentMethod or DeliveryAddress subclass")

    def get_serializer(self, instance):
        return self.get_serializer_class(instance)(instance)

registry = LineItemSerializerRegistry()


class WritableSerializerMethodField(fields.SerializerMethodField):

    def __init__(self, write_serializer, method_name=None, **kwargs):
        self.method_name = method_name
        self.write_serializer = write_serializer
        kwargs['source'] = '*'
        super(fields.SerializerMethodField, self).__init__(**kwargs)

    def to_internal_value(self, representation):
        return {self.field_name: self.write_serializer.to_representation(representation)}


class PrimaryKeyModelSerializer(serializers.ModelSerializer):
    """A serializer that accepts the primary key of an object as input.

    When read from, this serializer works exactly the same as ModelSerializer.
    When written to, it accepts a valid primary key of an existing instance
    of the same model. It can't be used to add or edit model instances.

    This is provided as a convenience, for the common use case of a
    :class:`~lorikeet.models.LineItem` subclass that has a foreign key to
    a product model; see the :doc:`Getting Started Guide <backend>` for a
    usage example.
    """

    def get_queryset(self):
        """Returns a queryset which the model instance is retrieved from.

        By default, returns ``self.Meta.model.objects.all()``.
        """
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
    data = WritableSerializerMethodField(fields.DictField())
    total = fields.SerializerMethodField()
    url = fields.SerializerMethodField()

    def get_total(self, instance):
        return str(instance.get_total())

    def get_url(self, instance):
        return reverse('lorikeet:cart-item', kwargs={'id': instance.id})

    def update(self, instance, validated_data):
        ser = registry.get_serializer(instance)
        return ser.update(instance, validated_data['data'])


class DeliveryAddressSerializer(RegistryRelatedWithMetadataSerializer):
    selected = WritableSerializerMethodField(fields.BooleanField())
    url = fields.SerializerMethodField()

    def get_selected(self, instance):
        return instance.id == self.context['cart'].delivery_address_id

    def get_url(self, instance):
        return reverse('lorikeet:address', kwargs={'id': instance.id})

    def update(self, instance, validated_data):
        if validated_data['selected']:
            cart = self.context['cart']
            cart.delivery_address = instance
            cart.save()
        return instance


class PaymentMethodSerializer(RegistryRelatedWithMetadataSerializer):
    selected = WritableSerializerMethodField(fields.BooleanField())
    url = fields.SerializerMethodField()

    def get_selected(self, instance):
        return instance.id == self.context['cart'].payment_method_id

    def update(self, instance, validated_data):
        if validated_data['selected']:
            cart = self.context['cart']
            cart.payment_method = instance
            cart.save()
        return instance

    def get_url(self, instance):
        return reverse('lorikeet:payment-method', kwargs={'id': instance.id})


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
    grand_total = fields.DecimalField(
        max_digits=7, decimal_places=2, source='get_grand_total')
    is_complete = fields.SerializerMethodField()
    incomplete_reasons = fields.SerializerMethodField()
    is_authenticated = fields.SerializerMethodField()
    checkout_url = fields.SerializerMethodField()
    generated_at = fields.SerializerMethodField()
    email = fields.EmailField()

    def get_new_item_url(self, _):
        return reverse('lorikeet:add-to-cart')

    def get_new_address_url(self, _):
        return reverse('lorikeet:new-address')

    def get_delivery_addresses(self, cart):
        selected = cart.delivery_address_subclass
        the_set = []

        if cart.user:
            the_set = cart.user.delivery_addresses.filter(
                active=True).select_subclasses()

        if selected is not None and selected not in the_set:
            the_set = chain(the_set, [selected])

        return DeliveryAddressSerializer(instance=the_set, many=True, context={'cart': cart}).data

    def get_new_payment_method_url(self, _):
        return reverse('lorikeet:new-payment-method')

    def get_payment_methods(self, cart):
        the_set = []
        selected = cart.payment_method_subclass

        if cart.user:
            the_set = cart.user.paymentmethod_set.filter(
                active=True).select_subclasses()

        if selected is not None and selected not in the_set:
            the_set = chain(the_set, [selected])

        return PaymentMethodSerializer(instance=the_set, many=True, context={'cart': cart}).data

    def get_generated_at(self, cart):
        return time()

    def get_is_complete(self, cart):
        return cart.is_complete()

    def get_incomplete_reasons(self, cart):
        return cart.errors.to_json()

    def get_is_authenticated(self, cart):
        return cart.user_id is not None

    def get_checkout_url(self, _):
        return reverse('lorikeet:checkout')

    class Meta:
        model = models.Cart
        fields = ('items', 'new_item_url', 'delivery_addresses',
                  'new_address_url', 'payment_methods',
                  'new_payment_method_url', 'grand_total', 'generated_at',
                  'is_complete', 'incomplete_reasons', 'checkout_url',
                  'is_authenticated', 'email')


class CartUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating the cart; used only for email field."""

    class Meta:
        model = models.Cart
        fields = ('email',)


class LineItemSerializer(serializers.ModelSerializer):
    """Base serializer for LineItem subclasses."""

    def __init__(self, instance=None, *args, **kwargs):
        if 'cart' in kwargs:
            self.cart = kwargs.pop('cart')
        elif instance is not None:
            self.cart = instance.cart
        else:
            raise TypeError("Either instance or cart arguments must be "
                            "provided to {}".format(self.__class__.__name__))
        return super().__init__(instance, *args, **kwargs)

    def create(self, validated_data):
        validated_data['cart'] = self.cart
        return super().create(validated_data)
