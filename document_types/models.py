from django.db import models


class DocumentType(models.Model):
    name: models.CharField = models.CharField(max_length=250, verbose_name="Nombre")
    code: models.CharField = models.CharField(max_length=10, verbose_name="Código")

    def __str__(self):
        return self.name
