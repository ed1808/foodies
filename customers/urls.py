from django.urls import path

from .views import (
    CustomersListView,
    CustomerDetailView,
    CustomerDeleteView,
    CustomerUpdateView,
    CustomerCreateView,
    CustomersAPIView,
)

urlpatterns = [
    path("", CustomersListView.as_view(), name="customers"),
    path("<int:id>", CustomerDetailView.as_view(), name="detail_customer"),
    path("api/", CustomersAPIView.as_view(), name="api_customers"),
    path("create-customer/", CustomerCreateView.as_view(), name="add_customer"),
    path(
        "delete-customer/<int:id>", CustomerDeleteView.as_view(), name="delete_customer"
    ),
    path(
        "update-customer/<int:id>", CustomerUpdateView.as_view(), name="update_customer"
    ),
]
