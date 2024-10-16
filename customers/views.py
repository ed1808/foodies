from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .forms import CustomerForm
from .models import Customer
from companies.models import Company


class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    template_name = "create_customer.html"
    success_url = reverse_lazy("customers")
    form_class = CustomerForm

    def form_valid(self, form):
        # form.instance.company = self.request.user.company
        company = Company.objects.get(id=1)
        form.save(commit=False)
        form.instance.companies.set(company)
        form.save_m2m()
        return super().form_valid(form)


class CustomersListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = "customers.html"
    context_object_name = "customers"

    def get_queryset(self) -> QuerySet[Any]:
        return Customer.objects.filter(companies__id=1)


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = "detail_customer.html"
    context_object_name = "customer"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return (
            Customer.objects.filter(id=self.kwargs["id"])
            .values("id", "name", "phone_number", "address", "neighborhood")
            .first()
        )


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = "delete_customer.html"
    success_url = reverse_lazy("customers")
    context_object_name = "customer"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return (
            Customer.objects.filter(id=self.kwargs["id"])
            .values("id", "name", "phone_number", "address", "neighborhood")
            .first()
        )


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "update_customer.html"
    context_object_name = "customer"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return Customer.objects.get(id=self.kwargs["id"])

    def get_success_url(self) -> str:
        return reverse_lazy("detail_customer", kwargs={"id": self.object.id})
