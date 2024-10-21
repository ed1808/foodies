from django.contrib.auth.models import User
from django.db import models

from companies.models import Company
from customers.models import Customer
from products.models import Product


class Order(models.Model):
    attended_by: models.ForeignKey = models.ForeignKey(User, on_delete=models.PROTECT)
    customer: models.ForeignKey = models.ForeignKey(Customer, on_delete=models.PROTECT)
    company: models.ForeignKey = models.ForeignKey(Company, on_delete=models.PROTECT)
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha hora solicitud"
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True, verbose_name="Fecha hora actualización"
    )

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self) -> str:
        return f"Orden #{self.id}"


class OrderDetail(models.Model):
    order: models.ForeignKey = models.ForeignKey(Order, on_delete=models.CASCADE)
    product: models.ForeignKey = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity: models.PositiveIntegerField = models.PositiveIntegerField(
        verbose_name="Cantidad"
    )

    class Meta:
        verbose_name = "Detalle del pedido"
        verbose_name_plural = "Detalles de los pedidos"

    def __str__(self) -> str:
        return f"Detalle del pedido #{self.id}"
