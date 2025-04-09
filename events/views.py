from rest_framework import permissions, viewsets

from .models import Event, Ticket
from .premissions import OrganizationOwnerPermission
from .serializer import EventCreateSerializer, EventSerializer, TicketSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.get_all_events()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, OrganizationOwnerPermission]

    def get_serializer_class(self):
        match self.action:
            case "create":
                return EventCreateSerializer
            case _:
                return EventSerializer


class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs["event_id"]
        return Ticket.objects.filter(event=event_id)

    def get_serializer_class(self):
        match self.action:
            case "create":
                return TicketSerializer
            case _:
                return TicketSerializer
