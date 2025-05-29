from rest_framework import permissions
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView

from .models import Organization
from .permissions import IsOwnerOrReadOnly
from .serializer import OrganizationCreateSerializer, OrganizationSerializer


class OrganizationCreateView(ListCreateAPIView):
    queryset = Organization.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrganizationCreateSerializer
        return OrganizationSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class OrganizationDetailView(RetrieveUpdateAPIView):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_field = "id"
    lookup_url_kwarg = "org_id"

    def get_serializer_class(self):
        if self.request.method == "PATCH" or self.request.method == "PUT":
            return OrganizationCreateSerializer
        return OrganizationSerializer
