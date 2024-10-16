from django.forms import ModelForm, TextInput, Textarea, NumberInput, FileInput, Select

from .models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        exclude = ["company"]
        widgets = {
            "name": TextInput(
                attrs={
                    "class": "p-3 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded focus:ring-orange-600 focus:border-orange-600 block w-full",
                    "placeholder": "Escribe el nombre del producto",
                }
            ),
            "description": Textarea(
                attrs={
                    "class": "p-3 block w-full text-sm text-gray-900 bg-gray-50 rounded border border-gray-300 focus:ring-orange-500 focus:border-orange-500",
                    "placeholder": "Escribe la descripción del producto",
                }
            ),
            "price": NumberInput(
                attrs={
                    "class": "p-3 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded focus:ring-orange-600 focus:border-orange-600 block w-full",
                    "placeholder": "10000",
                }
            ),
            "picture": FileInput(
                attrs={
                    "class": "p-3 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded focus:ring-orange-600 focus:border-orange-600 block w-full",
                }
            ),
            "stock": NumberInput(
                attrs={
                    "class": "p-3 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded focus:ring-orange-600 focus:border-orange-600 block w-full",
                    "placeholder": "10",
                }
            ),
            "category": Select(
                attrs={
                    "class": "p-3 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded focus:ring-orange-500 focus:border-orange-500 block w-full",
                }
            ),
        }
