import sentry_sdk
from decouple import config

from .base import *  # noqa: F403
from .base import ALLOWED_HOSTS, REST_FRAMEWORK

ALLOWED_HOSTS += ["hamgerd.ir", "api.hamgerd.ir"]

REST_FRAMEWORK_PRODUCTION = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "10/minute", "user": "1000/day"},
}

REST_FRAMEWORK.update(REST_FRAMEWORK_PRODUCTION)

SENTRY_DSN = config("SENTRY_DSN", default=None)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        send_default_pii=False,
        traces_sample_rate=0.05,
        profile_session_sample_rate=0,
        profile_lifecycle="trace",
    )
