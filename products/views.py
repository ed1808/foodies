from typing import Any
from django.views.generic.base import TemplateView

from .models import Product


class ProductsView(TemplateView):
    template_name = "products.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        products = Product.objects.all()

        return {"products": products}
