from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from ..models import Event, Speaker
from ..permissions import IsOrganizationOwnerThroughPermission
from ..serializers import (
    SpeakerSerializer,
)
from .common import public_event_id_parameter


@extend_schema_view(
    create=extend_schema(parameters=[public_event_id_parameter]),
    retrieve=extend_schema(parameters=[public_event_id_parameter]),
    update=extend_schema(parameters=[public_event_id_parameter]),
    partial_update=extend_schema(parameters=[public_event_id_parameter]),
    destroy=extend_schema(parameters=[public_event_id_parameter]),
    list=extend_schema(parameters=[public_event_id_parameter]),
)
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
