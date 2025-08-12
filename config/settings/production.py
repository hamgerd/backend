import sentry_sdk
from decouple import config
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F403
from .base import ALLOWED_HOSTS, REST_FRAMEWORK

ALLOWED_HOSTS += ["hamgerd.ir", "api.hamgerd.ir", "localhost"]
CSRF_TRUSTED_ORIGINS = ["https://api.hamgerd.ir", "https://hamgerd.ir"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://hamgerd.ir",
    "https://api.hamgerd.ir",
]

REST_FRAMEWORK_PRODUCTION = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "10/minute", "user": "1000/day"},
}

REST_FRAMEWORK.update(REST_FRAMEWORK_PRODUCTION)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": config("DJANGO_LOG_LEVEL", "DEBUG"),
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "django_app.log",
            "maxBytes": 1024 * 1024 * 5,  # 5MB
            "backupCount": 5,
            "formatter": "verbose",
            "level": "WARNING",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": config("DJANGO_LOG_LEVEL", "WARNING"),
            "propagate": True,
        },
    },
}

SENTRY_DSN = config("SENTRY_DSN", default=None)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        send_default_pii=False,
        traces_sample_rate=0.05,
        profile_session_sample_rate=0,
        profile_lifecycle="trace",
        integrations=[DjangoIntegration(), CeleryIntegration()],
    )

ATOMIC_REQUESTS = True

AWS_S3_USE_SSL = True
AWS_S3_ADDRESSING_STYLE = "path"
