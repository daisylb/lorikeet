from django.http import Http404
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from . import api_serializers, models


class CartView(APIView):

    def get(self, request, format=None):
        cart = request.get_cart()
        data = api_serializers.CartSerializer(
            cart, context={'request': self.request}).data
        return Response(data)


class CartItemView(RetrieveUpdateDestroyAPIView):

    def get_object(self):
        cart = self.request.get_cart()
        try:
            return cart.items.get_subclass(id=self.kwargs['id'])
        except models.LineItem.DoesNotExist:
            raise Http404()

    def get_serializer(self, instance, *args, **kwargs):
        return api_serializers.LineItemMetadataSerializer(
            instance, context={'cart': self.request.get_cart()}, *args, **kwargs)


class AddToCartView(CreateAPIView):

    def get_serializer(self, data, *args, **kwargs):
        ser_class = api_serializers.registry.line_items[data['type']]
        return ser_class(data=data['data'], cart=self.request.get_cart(),
                         *args, **kwargs)


class NewAddressView(CreateAPIView):

    def get_serializer(self, data, *args, **kwargs):
        ser_class = api_serializers.registry.delivery_addresses[data['type']]
        return ser_class(data=data['data'], *args, **kwargs)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        cart = self.request.get_cart()
        cart.delivery_address = serializer.instance
        cart.save()


class NewPaymentMethodView(CreateAPIView):

    def get_serializer(self, data, *args, **kwargs):
        ser_class = api_serializers.registry.payment_methods[data['type']]
        return ser_class(data=data['data'],
                         context={'request': self.request},
                         *args, **kwargs)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        cart = self.request.get_cart()
        cart.payment_method = serializer.instance
        cart.save()


class PaymentMethodView(RetrieveUpdateDestroyAPIView):

    def get_object(self):
        try:
            assert self.request.user.is_authenticated()
            return models.PaymentMethod.objects.get_subclass(
                user=self.request.user, id=self.kwargs['id'])
        except (AssertionError, models.PaymentMethod.DoesNotExist):
            cart = self.request.get_cart()
            if int(self.kwargs['id']) == cart.payment_method_id:
                return cart.payment_method_subclass

        raise Http404()

    def perform_destroy(self, instance):
        instance.active = False
        instance.save()
        cart = self.request.get_cart()
        if cart.payment_method_id == instance.id:
            cart.payment_method = None
            cart.save()

    def get_serializer(self, instance, *args, **kwargs):
        return api_serializers.PaymentMethodSerializer(
            instance, context={'cart': self.request.get_cart()}, *args, **kwargs)


class DeliveryAddressView(RetrieveUpdateDestroyAPIView):

    def get_object(self):
        try:
            assert self.request.user.is_authenticated()
            return models.DeliveryAddress.objects.get_subclass(
                user=self.request.user, id=self.kwargs['id'])
        except (AssertionError, models.DeliveryAddress.DoesNotExist):
            cart = self.request.get_cart()
            if int(self.kwargs['id']) == cart.delivery_address_id:
                return cart.delivery_address_subclass

        raise Http404()

    def perform_destroy(self, instance):
        instance.active = False
        instance.save()
        cart = self.request.get_cart()
        if cart.delivery_address_id == instance.id:
            cart.delivery_address = None
            cart.save()

    def get_serializer(self, instance, *args, **kwargs):
        return api_serializers.DeliveryAddressSerializer(
            instance, context={'cart': self.request.get_cart()}, *args, **kwargs)
