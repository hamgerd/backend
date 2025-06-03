from django.urls import path
from . import views

app_name = "payment"

urlpatterns = [
    path("pay/<str:bill_id>/", views.pay_bill, name="pay"),
    path("verify/<str:authority>/", views.verify_payment, name="verify"),
]
