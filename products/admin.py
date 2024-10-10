from django.contrib import admin

from .models import Product


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ("name", "company", "category")
    search_fields = ("name", "company", "category")


admin.site.register(Product, ProductAdmin)
