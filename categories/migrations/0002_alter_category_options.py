# Generated by Django 5.1.1 on 2024-10-11 19:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Categoría', 'verbose_name_plural': 'Categorías'},
        ),
    ]
