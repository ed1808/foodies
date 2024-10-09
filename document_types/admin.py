from django.contrib import admin

from .models import DocumentType


class DocumentTypeAdmin(admin.ModelAdmin):
    model = DocumentType
    list_display = ("name", "code")
    search_fields = ("name", "code")


admin.site.register(DocumentType, DocumentTypeAdmin)
