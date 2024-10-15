from django.db import models

from companies.models import Company


class Customer(models.Model):
    name: models.CharField = models.CharField(max_length=255, verbose_name="Nombre")
    phone_number: models.CharField = models.CharField(
        max_length=30, verbose_name="Número de teléfono"
    )
    address: models.CharField = models.CharField(
        max_length=255, verbose_name="Dirección"
    )
    neighborhood: models.CharField = models.CharField(
        max_length=255, verbose_name="Barrio"
    )
    companies: models.ManyToManyField = models.ManyToManyField(Company)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self) -> str:
        return self.name
