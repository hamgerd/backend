from django.urls import path
from . import views

app_name = "payment"

urlpatterns = [
    path("pay/<str:transaction>/", views.PayTransactionView.as_view(), name="pay"),
    path("verify/<str:authority>/", views.VerifyPaymentView.as_view(), name="verify"),
]
