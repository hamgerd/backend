from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS += ["0.0.0.0", "127.0.0.1", "localhost"]
AWS_S3_PROXIES = {"http": "minio:9000"}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK_BASE = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}

REST_FRAMEWORK.update(REST_FRAMEWORK_BASE)

INSTALLED_APPS += [
    'django_extensions',
]

PAYMENT_PORTAL_BASE_URL = "https://sandbox.zarinpal.com/"
CALLBACK_URL = 'https://test.hamgerd.ir/verify/'