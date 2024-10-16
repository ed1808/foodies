from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserChangeForm
from django.contrib.auth.models import User
from django.forms import CharField, PasswordInput, TextInput


class LoginForm(AuthenticationForm):
    username = UsernameField(
        widget=TextInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 rounded-lg focus:ring-orange-600 focus:border-orange-600 block w-full p-2.5",
                "placeholder": "miusuario123",
            }
        )
    )

    password = CharField(
        widget=PasswordInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 rounded-lg focus:ring-orange-600 focus:border-orange-600 block w-full p-2.5",
                "placeholder": "••••••••",
            }
        )
    )


class EmployeeUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": TextInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 rounded-lg focus:ring-orange-600 focus:border-orange-600 block w-full p-2.5",
                    "placeholder": "Nombre",
                }
            ),
            "last_name": TextInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 rounded-lg focus:ring-orange-600 focus:border-orange-600 block w-full p-2.5",
                    "placeholder": "Apellido",
                }
            ),
            "email": TextInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 rounded-lg focus:ring-orange-600 focus:border-orange-600 block w-full p-2.5",
                    "placeholder": "correo@gmail.com",
                }
            ),
        }
