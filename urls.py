from django.conf.urls import url, include
from . import api_views

urlpatterns = [
    url(r'^cart/$', api_views.CartView.as_view(), name='cart'),
    url(r'^cart/(?P<id>\d+)/$', api_views.CartItemView.as_view(), name='cart-item')
]
