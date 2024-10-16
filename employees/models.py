from django.contrib.auth.models import User
from django.db import models

from companies.models import Company


class Employee(models.Model):
    user: models.OneToOneField = models.OneToOneField(User, on_delete=models.CASCADE)
    company: models.ForeignKey = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"

    def __str__(self) -> str:
        return self.user.username
