from rest_framework import permissions


class OrganizationOwnerPermission(permissions.BasePermission):
    """
    Custom permission to only allow owners of an organization to modify it.
    """

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
