from django.views.generic.base import TemplateView


class ProductsView(TemplateView):
    template_name = "products.html"
