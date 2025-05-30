from rest_framework.routers import DefaultRouter
from . import views

app_name = "payment"

router = DefaultRouter()

router.register("transaction/pay/<str:bill_id>", views.pay_bill, basename="payment")
router.register("transaction/verify/<str:authority>", views.verify_payment, basename="payment")
