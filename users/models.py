from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext


class User(AbstractUser):
    email = models.EmailField(gettext("email address"), blank=True, unique=True)
