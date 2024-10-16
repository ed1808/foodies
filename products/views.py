from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from .forms import ProductForm
from .models import Product

from companies.models import Company


class ProductsListView(ListView):
    model = Product
    template_name = "products.html"
    context_object_name = "products"

    def get_queryset(self) -> QuerySet[Any]:
        return Product.objects.filter(company__id=1)


class ProductDetailView(DetailView):
    model = Product
    template_name = "detail_product.html"
    context_object_name = "product"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return (
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


class CreateProductView(CreateView):
    model = Product
    template_name = "create_product.html"
    success_url = reverse_lazy("products")
    form_class = ProductForm

    def form_valid(self, form):
        # form.instance.company = self.request.user.company
        company = Company.objects.get(id=1)
        form.instance.company = company
        form.save()
        return super().form_valid(form)


class UpdateProductView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "update_product.html"
    context_object_name = "product"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return Product.objects.get(id=self.kwargs["id"])

    def get_success_url(self) -> str:
        return reverse_lazy("detail_product", kwargs={"id": self.object.id})


class DeleteProductView(DeleteView):
    model = Product
    template_name = "delete_product.html"
    success_url = reverse_lazy("products")
    context_object_name = "product"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return Product.objects.get(id=self.kwargs["id"])
