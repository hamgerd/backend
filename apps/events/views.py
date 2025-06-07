from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Event, Speaker, Ticket
from .permissions import IsOrganizationOwnerThroughPermission, OrganizationOwnerPermission
from .serializers import (
    EventCreateSerializer,
    EventSerializer,
    SpeakerSerializer,
    TicketCreateSerializer,
    TicketSerializer,
)
from .serializers.ticket import TicketCreateResponseSerializer
from .services.tickets import TicketCreationService


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.get_all_events()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, OrganizationOwnerPermission]
    lookup_field = "public_id"
    lookup_url_kwarg = "public_id"

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


class TicketViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "public_id"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Ticket.objects.none()

        event_id = self.kwargs["event_id"]
        return Ticket.objects.filter(event=event_id)

    def get_serializer_class(self):
        if self.action == "create_by_type":
            return TicketCreateSerializer
        else:
            return TicketSerializer

    @swagger_auto_schema(
        request_body=TicketCreateSerializer(many=True),
        responses={201: TicketCreateResponseSerializer()},
    )
    @action(methods=["post"], detail=False)
    def create_by_type(self, request, event_public_id=None):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        event = get_object_or_404(Event, public_id=event_public_id)
        response_serializer = TicketCreationService.handle_ticket_creation(
            event, request.user, serializer.validated_data
        )
        return Response(response_serializer.data, status.HTTP_201_CREATED)


class SpeakerViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SpeakerSerializer
    lookup_field = "public_id"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Speaker.objects.none()

        event_id = self.kwargs["event_public_id"]
        return Speaker.objects.filter(event__public_id=event_id)

    def get_permissions(self):
        if self.action in ["retrieve", "list"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOrganizationOwnerThroughPermission()]

    def create(self, request, event_pk=None):
        """Create a new speaker for a specific event"""
        event = self.get_event(request.user, event_pk)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, **kwargs):
        """Update an existing speaker for a specific event"""
        speaker = self.get_object()
        serializer = self.serializer_class(speaker, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_event(user, event_pk):
        """Get the provided event_pk if the organization owner is the provided user"""
        try:
            return Event.objects.filter(organization__owner=user).get(pk=event_pk)
        except Event.DoesNotExist:
            raise NotFound("Event was not found or doesn't belong to you.")


class UserTicketsView(GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_tickets = Ticket.objects.select_related("user").filter(user=request.user)
        serializer = self.get_serializer(user_tickets, many=True)
        return Response(serializer.data)
