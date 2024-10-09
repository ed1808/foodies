from django.db import models

from document_types.models import DocumentType


class Company(models.Model):
    name: models.CharField = models.CharField(
        max_length=250, verbose_name="Nombre de la empresa"
    )
    email: models.EmailField = models.EmailField(verbose_name="Correo electrónico")
    phone: models.CharField = models.CharField(max_length=20, verbose_name="Teléfono")
    document_number: models.CharField = models.CharField(
        max_length=20, verbose_name="Número de documento"
    )
    document_type: models.ForeignKey = models.ForeignKey(
        DocumentType, on_delete=models.PROTECT, verbose_name="Tipo de documento"
    )
    address: models.TextField = models.TextField(verbose_name="Dirección")
    city: models.CharField = models.CharField(max_length=100, verbose_name="Ciudad")
    country: models.CharField = models.CharField(max_length=100, verbose_name="País")

    def __str__(self) -> str:
        return self.name
