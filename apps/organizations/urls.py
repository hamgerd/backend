from django.urls import path

from . import views

app_name = "organizations"

urlpatterns = [
    path("", views.OrganizationListView.as_view(), name="organization-list"),
    path("<int:org_id>", views.get_org, name="organization_entity"),
]
