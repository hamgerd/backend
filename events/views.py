from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Event
from .serializer import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.get_all_events()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
