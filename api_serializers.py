from rest_framework import serializers, fields
from . import models
from django.core.urlresolvers import reverse

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
        self.Meta.model.objects.all()

    def to_internal_value(self, repr):
        return self.get_queryset().get(pk=repr)


class RegistryRelatedField(fields.Field):
    def to_representation(self, instance):
        return registry.get_serializer(instance).data


class LineItemSerializer(serializers.Serializer):
    type = fields.CharField()
    data = RegistryRelatedField()
    total = fields.DecimalField(max_digits=7, decimal_places=2)
    url = fields.URLField()

    def to_representation(self, instance):
        return {
            'type': self.fields['type'].to_representation(instance.__class__.__name__),
            'data': self.fields['data'].to_representation(instance),
            'total': self.fields['total'].to_representation(instance.get_total()),
            'url': self.fields['url'].to_representation(reverse('cart:cart-item', kwargs={'id': instance.id})),
        }


class SubclassListSerializer(serializers.ListSerializer):
    def to_representation(self, instance, *args, **kwargs):
        instance = instance.select_subclasses()
        return super().to_representation(instance, *args, **kwargs)


class CartSerializer(serializers.ModelSerializer):
    items = SubclassListSerializer(child=LineItemSerializer())
    new_item_url = fields.SerializerMethodField()
    grand_total = fields.DecimalField(max_digits=7, decimal_places=2, source='get_grand_total')

    def get_new_item_url(self, _):
        return reverse('cart:add-to-cart')

    class Meta:
        model = models.Cart
        fields = ('items', 'new_item_url', 'grand_total')


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
