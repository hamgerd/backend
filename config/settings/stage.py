from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS += ["0.0.0.0", "127.0.0.1", "localhost", "stage.hamgerd.ir"]
AWS_S3_PROXIES = {"http": "minio:9000"}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

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

# Minio
AWS_S3_ENDPOINT_URL = config("MINIO_STORAGE_ENDPOINT")
AWS_ACCESS_KEY_ID = config("MINIO_STORAGE_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = config("MINIO_STORAGE_SECRET_KEY")

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": config("MINIO_DEFAULT_STORAGE_BUCKET_NAME", "media"),
            "default_acl": "public-read",
            "file_overwrite": False,
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {"bucket_name": config("MINIO_STATIC_STORAGE_BUCKET_NAME", "static")},
    },
}

PAYMENT_PORTAL_BASE_URL = "https://sandbox.zarinpal.com/"
CALLBACK_URL = "https://test.hamgerd.ir/verify/"
