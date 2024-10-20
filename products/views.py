from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import ProductForm
from .models import Product
from .serializers import ProductSerializer, ProductsSerializer


class ProductsListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "products.html"
    context_object_name = "products"

    def get_queryset(self) -> QuerySet[Any]:
        return Product.objects.filter(company=self.request.user.employee.company)


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "detail_product.html"
    context_object_name = "product"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        product = (
            Product.objects.filter(id=self.kwargs["id"])
            .values(
                "id",
                "name",
                "description",
                "price",
                "stock",
                "picture",
                "category__name",
            )
            .first()
        )

        if product is None:
            raise Http404("Producto no encontrado")

        return product


class CreateProductView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = "create_product.html"
    success_url = reverse_lazy("products")
    form_class = ProductForm

    def form_valid(self, form):
        form.instance.company = self.request.user.employee.company
        form.save()
        return super().form_valid(form)


class UpdateProductView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "update_product.html"
    context_object_name = "product"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        product = get_object_or_404(Product, id=self.kwargs["id"])

        return product

    def get_success_url(self) -> str:
        return reverse_lazy("detail_product", kwargs={"id": self.object.id})


class DeleteProductView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = "delete_product.html"
    success_url = reverse_lazy("products")
    context_object_name = "product"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        product = get_object_or_404(Product, id=self.kwargs["id"])

        return product


class ProductsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        products = Product.objects.filter(company=request.user.employee.company)
        serializer = ProductsSerializer(products, many=True)

        return Response(serializer.data)


class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        product = get_object_or_404(Product, id=pk)

        return product

    def get(self, request, id, format=None):
        product = self.get_object(id)
        serializer = ProductSerializer(product)

        return Response(serializer.data)
