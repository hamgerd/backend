from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotAcceptable, PermissionDenied
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Event, Ticket
from ..serializers import (
    TicketCreateSerializer,
    TicketSerializer,
)
from ..serializers.ticket import TicketCreateResponseSerializer
from ..services.tickets import TicketCreationService
from .common import public_event_id_parameter, public_ticket_id_parameter


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
    pagination_class = PageNumberPagination

    @extend_schema(
        responses={
            200: inline_serializer(
                name="PaginatedTicketResponse",
                fields={
                    "count": serializers.IntegerField(),
                    "next": serializers.CharField(allow_null=True),
                    "previous": serializers.CharField(allow_null=True),
                    "results": TicketSerializer(many=True),
                },
            )
        },
        parameters=[
            OpenApiParameter(
                "page",
                description="A page number within the paginated result set.",
                type=OpenApiTypes.INT,
                location="query",
            )
        ],
    )
    def get(self, request):
        queryset = Ticket.objects.select_related("user").filter(user=request.user)
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


@extend_schema_view(
    create=extend_schema(parameters=[public_event_id_parameter, public_ticket_id_parameter]),
    retrieve=extend_schema(parameters=[public_event_id_parameter, public_ticket_id_parameter]),
    key=extend_schema(parameters=[public_event_id_parameter, public_ticket_id_parameter]),
)
class UserPresenceView(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = "public_id"

    def retrieve(self, request, pk):
        ticket = get_object_or_404(Ticket, public_id=pk)
        if request.user in [ticket.user, ticket.ticket_type.event.organization.owner]:
            return Response({"presence": ticket.presence})
        else:
            raise PermissionDenied("You do not have permission.")

    def create(self, request, pk):
        ticket = get_object_or_404(Ticket, public_id=pk)
        presence_key = request.data.get("presence_key")

        if request.user == ticket.ticket_type.event.organization.owner:
            if ticket.user_attended(presence_key):
                return Response({"message": "user presence registered"})
            else:
                raise NotAcceptable("wrong presence_key")
        else:
            raise PermissionDenied("You do not have permission.")

    @action(methods=["post"], detail=True)
    def key(self, request, pk):
        ticket = get_object_or_404(Ticket, public_id=pk)
        if request.user == ticket.user:
            return Response({"presence": ticket.presence_key})
        else:
            raise PermissionDenied("You do not have permission.")
