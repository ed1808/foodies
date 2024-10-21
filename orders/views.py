from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models.base import Model as Model
from django.db.transaction import atomic
from django.db.models import F
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from customers.models import Customer
from products.models import Product

from .models import Order, OrderDetail


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders.html"
    context_object_name = "orders"

    def get_queryset(self) -> QuerySet[Any]:
        return Order.objects.filter(company=self.request.user.employee.company)


class OrderDetailView(LoginRequiredMixin, ListView):
    model = OrderDetail
    template_name = "detail_order.html"
    context_object_name = "order_detail"

    def get_queryset(self) -> QuerySet[Any]:
        return OrderDetail.objects.filter(order_id=self.kwargs["id"])


class OrderCreateView(LoginRequiredMixin, TemplateView):
    template_name = "create_order.html"


class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        items = request.data["items"]
        customer_id = request.data["customer"]

        try:
            with atomic():
                customer = Customer.objects.get(id=customer_id)

                order = Order.objects.create(
                    attended_by=request.user,
                    customer=customer,
                    company=request.user.employee.company,
                )

                for item in items:
                    product_id = item["product"]
                    quantity = int(item["quantity"])

                    product = Product.objects.get(id=product_id)

                    if product.stock < quantity:
                        raise ValidationError("Product out of stock")

                    product.stock = F("stock") - quantity
                    product.save()

                    OrderDetail.objects.create(
                        order=order, product=product, quantity=quantity
                    )

                return Response(
                    {"status": "success", "message": "Order created successfully"}
                )
        except ValidationError as e:
            return Response({"status": "error", "message": e.message})
        except Exception as e:
            return Response({"status": "error", "message": str(e)})
