from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Event.get_all_events()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, OrganizationOwnerPermission]

    def get_serializer_class(self):
        match self.action:
            case "create":
                return EventCreateSerializer
            case _:
                return EventSerializer

    @action(methods=["get"], detail=False)
    def featured(self, request):
        """Get all upcoming events"""
        queryset = Event.get_featured_events()
        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data)