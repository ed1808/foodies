from django.urls import path

from .views import OrderListView, OrderCreateView, OrderCreateAPIView, OrderDetailView

urlpatterns = [
    path("", OrderListView.as_view(), name="orders"),
    path("add-order/", OrderCreateView.as_view(), name="create_order"),
    path("api/add-order/", OrderCreateAPIView.as_view(), name="create_order_api"),
    path("order-details/<int:id>/", OrderDetailView.as_view(), name="detail_order"),
]
