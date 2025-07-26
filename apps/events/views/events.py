from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..filters import EventFilter
from ..models import Event
from ..permissions import OrganizationOwnerPermission
from ..serializers import (
    EventCreateSerializer,
    EventSerializer,
)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.get_all_events()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, OrganizationOwnerPermission]
    lookup_field = "public_id"
    lookup_url_kwarg = "public_id"
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = EventFilter

    def get_serializer_class(self):
        match self.action:
            case "create":
                return EventCreateSerializer
            case _:
                return EventSerializer

    @action(methods=["get"], detail=False)
    def featured(self, request):
        """Get all upcoming events"""
        queryset = Event.get_featured_events()
        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data)
