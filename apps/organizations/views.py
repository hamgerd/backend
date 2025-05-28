from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .models import Organization
from .serializer import OrganizationCreateSerializer, OrganizationSerializer


@api_view(["GET"])
def get_org(request, org_id):
    """
    Retrieve a specific organization by ID
    """
    organization = get_object_or_404(Organization, id=org_id)
    serializer = OrganizationSerializer(organization)
    return Response(serializer.data)


class OrganizationListView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    def get_serializer_class(self):
        match self.request.method:
            case "POST":
                return OrganizationCreateSerializer
            case _:
                return OrganizationSerializer

    def get(self, request, format=None):
        """
        Return a list of all organizations.
        """
        organizations = Organization.get_all_organizations()
        serializer = self.serializer_class(organizations, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new organization.
        """
        serializer = OrganizationCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(self.serializer_class(serializer.instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, org_id):
        """
        Update an organization.
        """
        organization = get_object_or_404(Organization, id=org_id)

        # Check if user is the owner of the organization
        if organization.owner != request.user:
            return Response(
                {"detail": "You do not have permission to update this organization."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = OrganizationCreateSerializer(organization, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(self.serializer_class(serializer.instance).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, org_id):
        """
        Delete an organization.
        """
        organization = get_object_or_404(Organization, id=org_id)

        # Check if user is the owner of the organization
        if organization.owner != request.user:
            return Response(
                {"detail": "You do not have permission to delete this organization."}, status=status.HTTP_403_FORBIDDEN
            )

        organization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
