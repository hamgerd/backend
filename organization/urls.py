from django.urls import path

from . import views

app_name = "organization"

urlpatterns = [
    path("", views.OrganizationListView.as_view(), name="organization-list"),
    path("{org_id}/", views.get_org, name="organization_entity"),
]
