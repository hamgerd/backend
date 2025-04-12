from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import EmailVerifyView, UserRegisterView
from users.views.users import PasswordResetRequestView, PasswordResetView, UserMeView
from users.views.simplejwt import DecoratedTokenObtainPairView

app_name = "users"
urlpatterns = [
    path("me/", UserMeView.as_view(), name="me"),
    path("auth/token/", DecoratedTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("password-reset-request/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path("email/verify/<token>/", EmailVerifyView.as_view(), name="verify_mail"),
]
