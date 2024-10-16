from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from debug_toolbar import urls as debug_toolbar

if not settings.TESTING:
    urlpatterns = [
        path("", include("customers.urls")),
        path("admin/", admin.site.urls),
        path("products/", include("products.urls")),
        path("customers/", include("customers.urls")),
        path("employees/", include("employees.urls")),
        path("__debug__/", include(debug_toolbar)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns = [
        path("", include("customers.urls")),
        path("admin/", admin.site.urls),
        path("products/", include("products.urls")),
        path("customers/", include("customers.urls")),
        path("employees/", include("employees.urls")),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
