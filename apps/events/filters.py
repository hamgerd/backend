from django_filters import rest_framework as filters

from .models import Event


class EventFilter(filters.FilterSet):
    organization_username = filters.CharFilter(field_name="organization__username", lookup_expr="iexact")

    class Meta:
        model = Event
        fields = ["title"]
