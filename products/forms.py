from django.forms import ModelForm, TextInput, Textarea, NumberInput, FileInput, Select

from .models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        exclude = ["company"]
        widgets = {
            "name": TextInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded focus:ring-orange-600 focus:border-orange-600 block w-full",
                    "placeholder": "Escribe el nombre del producto",
                    "style": "padding: 0.75rem",
                }
            ),
            "description": Textarea(
                attrs={
                    "class": "block w-full text-sm text-gray-900 bg-gray-50 rounded border border-gray-300 focus:ring-orange-500 focus:border-orange-500",
                    "placeholder": "Escribe la descripción del producto",
                    "style": "padding: 0.75rem",
                }
            ),
            "price": NumberInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded focus:ring-orange-600 focus:border-orange-600 block w-full",
                    "placeholder": "10000",
                    "style": "padding: 0.75rem",
                }
            ),
            "picture": FileInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded focus:ring-orange-600 focus:border-orange-600 block w-full",
                    "style": "padding: 0.75rem",
                }
            ),
            "stock": NumberInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded focus:ring-orange-600 focus:border-orange-600 block w-full",
                    "placeholder": "10",
                    "style": "padding: 0.75rem",
                }
            ),
            "category": Select(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded focus:ring-orange-500 focus:border-orange-500 block w-full",
                    "style": "padding: 0.75rem",
                }
            ),
        }
