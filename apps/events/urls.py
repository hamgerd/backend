from django.urls import path
from rest_framework_nested import routers

from . import views

app_name = "events"

router = routers.SimpleRouter()
router.register("", views.EventViewSet, basename="event")

events_router = routers.NestedSimpleRouter(router, "", lookup="event")

events_router.register("tickets", views.TicketViewSet, basename="ticket")
events_router.register("speakers", views.SpeakerViewSet, basename="speaker")

urlpatterns = [
    *router.urls,
    *events_router.urls,
    path("tickets/me/", views.UserTicketsView.as_view(), name="user-tickets"),
]
