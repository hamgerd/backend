from rest_framework.decorators import api_view
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Organization


@api_view()
def get_org(request, org_id):
    return Response(Organization.get_organization_by_id(org_id))


class OrganizationListView(APIView):
    model = Organization
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        orgs_list = self.model.get_all_organizations()
        return Response(orgs_list)
