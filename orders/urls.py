from django.urls import path
from .views import OrderListCreateView, SellerOrderListView, DelegateShippingView

urlpatterns = [
    path('list-create/', OrderListCreateView.as_view(), name='order-list-create'),
    path('seller-orders/', SellerOrderListView.as_view(), name='seller-order-list'),
    path('<int:pk>/delegate-shipping/', DelegateShippingView.as_view(), name='delegate-shipping'),
]
