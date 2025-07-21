from django_filters import rest_framework as filters


class EventFilter(filters.FilterSet):
    organization_username = filters.CharFilter(field_name="organization__username", lookup_expr="iexact")
