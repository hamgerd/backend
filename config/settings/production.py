from .base import *

ALLOWED_HOSTS += ["hamgerd.ir"]

REST_FRAMEWORK_PRODUCTION = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "10/minute", "user": "1000/day"},
}

REST_FRAMEWORK.update(REST_FRAMEWORK_PRODUCTION)

PAYMENT_PORTAL_BASE_URL = "https://payment.zarinpal.com"
CALLBACK_URL = "https://hamgerd.ir/payment/verify/"
