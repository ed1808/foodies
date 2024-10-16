from django.contrib import admin

from .models import Employee


class EmployeeAdmin(admin.ModelAdmin):
    model = Employee


admin.site.register(Employee, EmployeeAdmin)
