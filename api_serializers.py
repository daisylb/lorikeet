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


class InheritanceRelatedField(fields.Field):
    def instance_to_representation(self, instance):
        return {
            'type': instance.__class__.__name__,
            'data': registry.get_serializer(instance).data,
            'total': instance.get_total(),
            'url': reverse('cart:cart-item', kwargs={'id': instance.id}),
        }

    def to_representation(self, internal_value):
        return [self.instance_to_representation(x)
                for x in internal_value.all().select_subclasses()]

class CartSerializer(serializers.ModelSerializer):
    items = InheritanceRelatedField()

    class Meta:
        model = models.Cart
        fields = ('items',)
