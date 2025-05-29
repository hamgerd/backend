from django.urls import path

from .views import (
    OrganizationCreateView,
    OrganizationDetailView,
)

app_name = "organizations"

urlpatterns = [
    path("", OrganizationCreateView.as_view(), name="organization-list"),
    path("<int:org_id>/", OrganizationDetailView.as_view(), name="organization-detail"),
]
