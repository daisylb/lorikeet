from django.conf.urls import url, include
from . import api_views

urlpatterns = [
    url(r'^cart/$', api_views.CartView.as_view(), name='cart'),
    url(r'^cart/(?P<id>\d+)/$', api_views.CartItemView.as_view(), name='cart-item'),
    url(r'^cart/new/$', api_views.AddToCartView.as_view(), name='add-to-cart'),
    url(r'^cart/new-address/$', api_views.NewAddressView.as_view(), name='new-address'),
]
