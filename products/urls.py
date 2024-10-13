from django.urls import path
from .views import ProductsListView, CreateProductView, DeleteProductView, ProductDetailView, UpdateProductView

urlpatterns = [
    path("", ProductsListView.as_view(), name="products"),
    path("product/<int:id>", ProductDetailView.as_view(), name="detail_product"),
    path("add-product/", CreateProductView.as_view(), name="add_product"),
    path("edit-product/<int:id>", UpdateProductView.as_view(), name="update_product"),
    path("delete-product/<int:id>", DeleteProductView.as_view(), name="delete_product"),
]
