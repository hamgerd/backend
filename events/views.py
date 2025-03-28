from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Event, Ticket, TicketType
from .serializer import EventSerializer, EventCreateSerializer
from organization.models import Organization

class OrganizationOwnerPermission(permissions.BasePermission):
    """
    Custom permission to only allow owners of an organization to modify it.
    """
    def has_permission(self, request, view):
        # Allow read operations for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # For write operations, check if organization is provided
        if not request.data.get('organization'):
            return False
            
        # Get the organization
        try:
            organization = Organization.objects.get(id=request.data['organization'])
            return organization.owner == request.user
        except Organization.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        # Allow read operations for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # For write operations, check if user owns the organization
        return obj.organization.owner == request.user


class TicketOwnerPermission(permissions.BasePermission):
    """
    Custom permission to only allow owners of an organization to modify it.
    """

    def has_permission(self, request, view):
        # Allow read operations for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True



        # For write operations, check if organization is provided
        if not view.kwargs["event_id"]:
            return False

        # Get the organization
        try:
            event = Event.objects.get(id=view.kwargs["event_id"])
            return event.organization in request.user.organizations
        except Organization.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        # Allow read operations for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations, check if user owns the organization
        return obj.organization.owner == request.user


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

