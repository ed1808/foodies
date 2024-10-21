from django.contrib import admin

from .models import Order, OrderDetail


class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    model = Order
    inlines = [OrderDetailInline]


admin.site.register(Order, OrderAdmin)
