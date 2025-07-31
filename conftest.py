import django
from django.conf import settings

from apps.events.tests.fixtures import *  # noqa: F403
from apps.organizations.tests.fixtures import *  # noqa: F403
from apps.payment.tests.fixtures import *  # noqa: F403
from apps.users.tests.fixtures import *  # noqa: F403


def pytest_configure():
    if not settings.configured:
        settings.configure()
    django.setup()
