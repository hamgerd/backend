from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

API_VERSION = "v1"


api_patterns = [
    path("organization/", include("apps.organizations.urls", namespace="organizations")),
    path("users/", include("apps.users.urls", namespace="users")),
    path("events/", include("apps.events.urls", namespace="events")),
    path("news/", include("apps.news.urls", namespace="news")),
    path("payment/", include("apps.payment.urls", namespace="payment")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="schema-swagger-ui"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"api/{API_VERSION}/", include(api_patterns)),
]
