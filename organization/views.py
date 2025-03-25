from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Organization


@api_view()
def get_org(request, org_id):
    return Response({"message": "Hello, world!"})


class OrganizationListView(APIView):
    model = Organization
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        orgs_list = self.model.get_all_organizations()
        return Response(orgs_list)
