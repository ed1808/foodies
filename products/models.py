from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models

from categories.models import Category
from companies.models import Company


class Product(models.Model):
    name: models.CharField = models.CharField(
        max_length=200, verbose_name="Nombre producto"
    )
    description: models.TextField = models.TextField(verbose_name="Descripción")
    price: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio",
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    picture: models.ImageField = models.ImageField(verbose_name="Imagen")
    stock: models.IntegerField = models.IntegerField(default=0, verbose_name="Stock")
    category: models.ForeignKey = models.ForeignKey(
        Category, on_delete=models.PROTECT, verbose_name="Categoría"
    )
    company: models.ForeignKey = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name="Empresa"
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.name
