from django.contrib import admin

from .models import Company


class CompanyAdmin(admin.ModelAdmin):
    model = Company
    list_display = ("name", "address", "phone", "email")
    search_fields = ("name", "address", "phone", "email")


admin.site.register(Company, CompanyAdmin)
