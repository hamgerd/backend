from rest_framework.routers import DefaultRouter

from . import views

app_name = "events"

router = DefaultRouter()
router.register("", views.EventViewSet, basename="events")
router.register("<int:event_id>/tickets", views.TicketViewSet, basename="tickets")

urlpatterns = router.urls
