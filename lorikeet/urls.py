from django.conf.urls import url

from . import api_views

urlpatterns = [
    url(r'^$', api_views.CartView.as_view(), name='cart'),
    url(r'^(?P<id>\d+)/$', api_views.CartItemView.as_view(), name='cart-item'),
    url(r'^new/$', api_views.AddToCartView.as_view(), name='add-to-cart'),
    url(r'^address/(?P<id>\d+)/$',
        api_views.DeliveryAddressView.as_view(),
        name='address'),
    url(r'^new-address/$', api_views.NewAddressView.as_view(), name='new-address'),
    url(r'^payment-method/(?P<id>\d+)/$',
        api_views.PaymentMethodView.as_view(),
        name='payment-method'),
    url(r'^new-payment-method/$',
        api_views.NewPaymentMethodView.as_view(), name='new-payment-method'),
    url(r'^checkout/$', api_views.CheckoutView.as_view(), name='checkout'),
]
