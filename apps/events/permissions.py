from rest_framework import permissions

from apps.organizations.models import Organization


class OrganizationOwnerPermission(permissions.BasePermission):
    """
    Custom permission to only allow owners of an organization to modify it.
    """

    def has_permission(self, request, view):
        # Allow read operations for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations, check if organization is provided
        if not request.data.get("organization"):
            return False

        # Get the organization
        try:
            organization = Organization.objects.get(id=request.data["organization"])
            return organization.owner == request.user
        except Organization.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        # Allow read operations for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations, check if user owns the organization
        return obj.organization.owner == request.user


class IsOrganizationOwnerThroughPermission(permissions.BasePermission):
    """Only allow organization owners modify event relateds"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.event.organization.owner == request.user
