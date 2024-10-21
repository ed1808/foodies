from rest_framework.serializers import ModelSerializer

from .models import Customer


class CustomersSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name"]
