from base import *

ALLOWED_HOSTS += ["hamgerd.ir"]

REST_FRAMEWORK_PRODUCTION = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "10/minute", "user": "1000/day"},
}

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

REST_FRAMEWORK.update(REST_FRAMEWORK_PRODUCTION)

PAYMENT_PORTAL_BASE_URL = "https://payment.zarinpal.com"
CALLBACK_URL = "https://hamgerd.ir/payment/verify/"
