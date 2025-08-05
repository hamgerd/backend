from django_filters import rest_framework as filters

from .models import Organization


class OrganizationFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Organization
        fields = ["name"]
