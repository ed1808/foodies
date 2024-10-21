from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .forms import CustomerForm
from .models import Customer
from .serializers import CustomersSerializer


class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    template_name = "create_customer.html"
    success_url = reverse_lazy("customers")
    form_class = CustomerForm

    def form_valid(self, form):
        new_customer = form.save(commit=False)
        new_customer.save()
        new_customer.companies.add(self.request.user.employee.company)

        return super().form_valid(form)


class CustomersListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = "customers.html"
    context_object_name = "customers"

    def get_queryset(self) -> QuerySet[Any]:
        return Customer.objects.filter(companies=self.request.user.employee.company)


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = "detail_customer.html"
    context_object_name = "customer"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        customer = get_object_or_404(Customer, id=self.kwargs["id"])

        return customer


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = "delete_customer.html"
    success_url = reverse_lazy("customers")
    context_object_name = "customer"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        customer = get_object_or_404(Customer, id=self.kwargs["id"])

        return customer


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "update_customer.html"
    context_object_name = "customer"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        customer = get_object_or_404(Customer, id=self.kwargs["id"])

        return customer

    def get_success_url(self) -> str:
        return reverse_lazy("detail_customer", kwargs={"id": self.object.id})


class CustomersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        customers = Customer.objects.filter(companies=request.user.employee.company)
        serializer = CustomersSerializer(customers, many=True)

        return Response(serializer.data)
