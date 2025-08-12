import pytest
from faker import Faker

from apps.users.models import User

faker = Faker()


@pytest.fixture
def user(db):
    return User.objects.create_user(email=faker.email(), password=faker.password())


@pytest.fixture
def another_user(db):
    return User.objects.create_user(email=faker.email(), password=faker.password())
