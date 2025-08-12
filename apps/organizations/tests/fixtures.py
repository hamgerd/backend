import pytest
from faker import Faker

from apps.organizations.models import Organization

faker = Faker()


@pytest.fixture
def organization(db, user):
    return Organization.objects.create(name=faker.word(), username=faker.user_name(), owner=user)
