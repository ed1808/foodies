from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .forms import LoginForm, EmployeeUpdateForm


class EmployeeLoginView(LoginView):
    template_name = "login.html"
    form_class = LoginForm

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("orders")
        return super().dispatch(request, *args, **kwargs)


class EmployeeListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "employees.html"
    context_object_name = "employees"

    def get_queryset(self) -> QuerySet[Any]:
        return User.objects.filter(
            employee__company=self.request.user.employee.company, is_active=True
        )


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EmployeeUpdateForm
    template_name = "update_employee.html"
    context_object_name = "employee"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return User.objects.get(id=self.kwargs["id"])

    def get_success_url(self) -> str:
        return reverse_lazy("detail_employee", kwargs={"id": self.object.id})


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "detail_employee.html"
    context_object_name = "employee"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        employee = get_object_or_404(User, id=self.kwargs["id"])

        return employee
