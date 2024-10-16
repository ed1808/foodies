from django.contrib import admin

from .models import Customer


class CustomerAdmin(admin.ModelAdmin):
    model = Customer
    list_display = ["name", "address", "neighborhood"]
    search_fields = ["name", "neighborhood"]


admin.site.register(Customer, CustomerAdmin)
