from django.forms import ModelForm, TextInput

from .models import Customer


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "phone_number", "address", "neighborhood"]
        widgets = {
            "name": TextInput(
                attrs={
                    "class": "p-3 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded focus:ring-orange-600 focus:border-orange-600 block w-full",
                    "placeholder": "John Doe",
                }
            ),
            "phone_number": TextInput(
                attrs={
                    "class": "p-3 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded focus:ring-orange-600 focus:border-orange-600 block w-full",
                    "placeholder": "3001112233",
                }
            ),
            "address": TextInput(
                attrs={
                    "class": "p-3 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded focus:ring-orange-600 focus:border-orange-600 block w-full",
                    "placeholder": "Calle 1 # 2 - 3",
                }
            ),
            "neighborhood": TextInput(
                attrs={
                    "class": "p-3 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded focus:ring-orange-600 focus:border-orange-600 block w-full",
                    "placeholder": "Robledo",
                }
            ),
        }
