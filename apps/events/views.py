from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Event, Ticket
from .premissions import OrganizationOwnerPermission
from .serializers import EventCreateSerializer, EventSerializer, TicketSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.get_all_events()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, OrganizationOwnerPermission]

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


class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Ticket.objects.none()

        event_id = self.kwargs["event_id"]
        return Ticket.objects.filter(event=event_id)

    def get_serializer_class(self):
        match self.action:
            case "create":
                return TicketSerializer
            case _:
                return TicketSerializer
