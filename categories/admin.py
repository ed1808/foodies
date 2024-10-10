from django.contrib import admin

from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ("name", "company")
    search_fields = ("name", "company")


admin.site.register(Category, CategoryAdmin)
