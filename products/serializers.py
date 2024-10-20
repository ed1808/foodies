from rest_framework.serializers import ModelSerializer

from .models import Product


class ProductsSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name"]


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ["price"]
