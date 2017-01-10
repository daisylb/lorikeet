from django.apps import AppConfig


class ShopConfig(AppConfig):
    name = 'shop'

    def ready(self):
        from . import models, api_serializers
        from lorikeet.api_serializers import registry

        registry.register(models.MyLineItem,
                          api_serializers.MyLineItemSerializer)
        registry.register(models.AustralianDeliveryAddress,
                          api_serializers.AustralianDeliveryAddressSerializer)
        registry.register(models.PipeCard,
                          api_serializers.PipeCardSerializer)
