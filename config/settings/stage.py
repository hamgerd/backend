from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS += ["0.0.0.0", "127.0.0.1", "localhost", "stage.hamgerd.ir", "api-stage.hamgerd.ir"]
AWS_S3_PROXIES = {"https": "api-stage.hamgerd.ir:9000"}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = ["https://stage.hamgerd.ir", "https://api-stage.hamgerd.ir"]

REST_FRAMEWORK_BASE = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "1000/day"},
}

REST_FRAMEWORK.update(REST_FRAMEWORK_BASE)

INSTALLED_APPS += [
    "django_extensions",
]

AWS_S3_USE_SSL = True
AWS_S3_ADDRESSING_STYLE = "path"