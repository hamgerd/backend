from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Event, Speaker, Ticket
from .premissions import OrganizationOwnerPermission
from .serializers import EventCreateSerializer, EventSerializer, SpeakerSerializer, TicketSerializer


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


class SpeakerViewSet(viewsets.ViewSet):
    serializer_class = SpeakerSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Speaker.objects.none()

        event_id = self.kwargs["event_pk"]
        return Speaker.objects.filter(event__id=event_id)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @swagger_auto_schema(responses={200: SpeakerSerializer(many=True)})
    def list(self, request, **kwargs):
        """List all speakers for a specific event"""
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: SpeakerSerializer(many=True)})
    def retrieve(self, request, pk=None, **kwargs):
        """List all speakers for a specific event"""
        queryset = self.get_queryset()
        speaker = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(speaker)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=SpeakerSerializer(), responses={200: SpeakerSerializer()})
    def create(self, request, event_pk=None):
        """Create a new speaker for a specific event"""
        event = self.get_event(request.user, event_pk)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data)
        return Response(serializer, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=SpeakerSerializer(), responses={200: SpeakerSerializer()})
    def partial_update(self, request, event_pk=None, pk=None):
        """Update an existing speaker for a specific event"""
        event = self.get_event(request.user, event_pk)
        queryset = self.get_queryset()
        speaker = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(speaker, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_event(user, event_pk):
        """Get the provided event_pk if the organization owner is the provided user"""
        try:
            return Event.objects.filter(organization__owner=user).get(pk=event_pk)
        except Event.DoesNotExist:
            raise NotFound("Event was not found or doesn't belong to you.")
