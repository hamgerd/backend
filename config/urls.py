from decouple import config
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

API_VERSION = config("API_VERSION")

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version=API_VERSION,
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

api_patterns = [
    path("organization/", include("apps.organizations.urls", namespace="organizations")),
    path("users/", include("apps.users.urls", namespace="users")),
    path("events/", include("apps.events.urls", namespace="events")),
    path("news/", include("apps.news.urls", namespace="news")),
    path("payment/", include("apps.payment.urls", namespace="payment")),
    path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"api/{API_VERSION}/", include(api_patterns)),
]
