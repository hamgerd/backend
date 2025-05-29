from rest_framework.routers import DefaultRouter

from . import views

app_name = "payment"

router = DefaultRouter()

router.register("bill/<int:event_id>", views.PaymentViewSet, basename="payment")
