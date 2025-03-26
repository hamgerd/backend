from rest_framework.decorators import api_view
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Organization
from .serializer import OrganizationSerializer, OrganizationCreateSerializer

@api_view()
def get_org(request, org_id):
    return Response(Organization.get_organization_by_id(org_id))


class OrganizationListView(APIView):
    model = Organization
    permission_classes = [permissions.IsAdminUser]
    # serializer_class = OrganizationSerializer
    def get(self, request, format=None):
        """
        Return a list of all organizations.
        """
        orgs_list = self.model.get_all_organizations()
        return Response(orgs_list)

    def post(self, request):
        """
        Create a new organization.
        """
        serializer = OrganizationCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Set the owner to the current user
            serializer.save(owner=request.user)
            # Return the full organization data using the main serializer
            return Response(
                OrganizationSerializer(serializer.instance).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
