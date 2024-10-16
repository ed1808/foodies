from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    EmployeeLoginView,
    EmployeeListView,
    EmployeeDetailView,
    EmployeeUpdateView,
)

urlpatterns = [
    path("login/", EmployeeLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", EmployeeListView.as_view(), name="employees"),
    path(
        "detail-employee/<int:id>", EmployeeDetailView.as_view(), name="detail_employee"
    ),
    path(
        "update-employee/<int:id>", EmployeeUpdateView.as_view(), name="update_employee"
    ),
]
