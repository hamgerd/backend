from django_filters import rest_framework as filters
from rest_framework import permissions
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from .filters import OrganizationFilter
from .models import Organization
from .permissions import IsOwnerOrReadOnly
from .serializer import OrganizationCreateSerializer, OrganizationSerializer


class OrganizationViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin):
    queryset = Organization.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = OrganizationFilter
    lookup_field = "username"
    lookup_url_kwarg = "org_username"

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return OrganizationCreateSerializer
        return OrganizationSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update"]:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
