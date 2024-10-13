from django.db import models


class DocumentType(models.Model):
    name: models.CharField = models.CharField(max_length=250, verbose_name="Nombre")
    code: models.CharField = models.CharField(max_length=10, verbose_name="Código")
    active: models.BooleanField = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Tipo de documento"
        verbose_name_plural = "Tipos de documentos"

    def __str__(self):
        return self.name
