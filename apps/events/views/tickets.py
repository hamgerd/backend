from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Event, Ticket
from ..serializers import (
    TicketCreateSerializer,
    TicketSerializer,
)
from ..serializers.ticket import TicketCreateResponseSerializer
from ..services.tickets import TicketCreationService
from .common import public_event_id_parameter


@extend_schema_view(
    retrieve=extend_schema(parameters=[public_event_id_parameter]),
    update=extend_schema(parameters=[public_event_id_parameter]),
    partial_update=extend_schema(parameters=[public_event_id_parameter]),
    list=extend_schema(parameters=[public_event_id_parameter]),
    create_by_type=extend_schema(parameters=[public_event_id_parameter]),
)
class TicketViewSet(
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

        event_id = self.kwargs["event_public_id"]
        return Ticket.objects.filter(ticket_type__event__public_id=event_id)

    def get_serializer_class(self):
        if self.action == "create_by_type":
            return TicketCreateSerializer
        else:
            return TicketSerializer

    @extend_schema(
        request=TicketCreateSerializer(many=True),
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


class UserTicketsView(GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_tickets = Ticket.objects.select_related("user").filter(user=request.user)
        serializer = self.get_serializer(user_tickets, many=True)
        return Response(serializer.data)
