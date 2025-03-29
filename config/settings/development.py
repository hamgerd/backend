from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS += ["0.0.0.0", "127.0.0.1", "localhost"]
AWS_S3_PROXIES = {"http": "minio:9000"}

CORS_ALLOW_ALL_ORIGINS = True