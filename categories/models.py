from django.db import models

from companies.models import Company


class Category(models.Model):
    name: models.CharField = models.CharField(
        max_length=200, verbose_name="Nombre categoria"
    )
    company: models.ForeignKey = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name="Empresa"
    )

    def __str__(self):
        return self.name
