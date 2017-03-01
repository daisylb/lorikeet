from logging import getLogger

from django.db.transaction import atomic
from django.http import Http404
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from . import api_serializers, exceptions, models

logger = getLogger(__name__)


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
        if self.request.user.is_authenticated():
            serializer.validated_data['user'] = self.request.user
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
        if self.request.user.is_authenticated():
            serializer.validated_data['user'] = self.request.user
        super().perform_create(serializer)
        cart = self.request.get_cart()
        cart.payment_method = serializer.instance
        cart.save()


class PaymentMethodView(RetrieveUpdateDestroyAPIView):

    def get_object(self):
        try:
            assert self.request.user.is_authenticated()
            return models.PaymentMethod.objects.get_subclass(
                user=self.request.user,
                id=self.kwargs['id'],
                active=True,
            )
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
                user=self.request.user,
                id=self.kwargs['id'],
                active=True,
            )
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


class CheckoutView(APIView):

    def post(self, request, format=None):
        try:
            with atomic():
                # Prepare the order object
                cart = request.get_cart()
                order = models.Order.objects.create(user=cart.user)

                # Check the cart is ready to be checked out
                cart.is_complete(raise_exc=True)

                # copy items onto order, also calculate grand total
                grand_total = 0
                for item in cart.items.select_subclasses().all():
                    total = item.get_total()
                    grand_total += total
                    item.total_when_charged = total
                    item.order = order
                    item.cart = None
                    item._new_order = True
                    item.save()

                # copy delivery address over
                order.delivery_address = cart.delivery_address

                # make payment and attach it to order
                order.payment = cart.payment_method_subclass.make_payment(
                    grand_total)
                print(order.payment)
                if not isinstance(order.payment, models.Payment):
                    raise TypeError(
                        "{}.make_payment() returned {!r}, not a Payment "
                        "subclass".format(
                            cart.payment_method.__class__.__name__,
                            order.payment,
                        )
                    )
                order.grand_total = grand_total
                order.save()
        except exceptions.PaymentError as e:
            return Response({
                'success': False,
                'reason': 'payment',
                'payment_method': cart.payment_method_subclass.__class__.__name__,
                'info': e.info,
            }, status=422)
        except exceptions.IncompleteCartErrorSet as e:
            return Response({
                'success': False,
                'reason': 'incomplete',
                'info': e.to_json(),
            }, status=422)
        else:
            return Response({
                'success': True,
                'id': order.id,
            }, status=200)
