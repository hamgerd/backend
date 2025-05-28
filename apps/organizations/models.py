from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.db import models

from apps.core.utils.identicon import add_profile_picture
from config.settings.base import AUTH_USER_MODEL


class Organization(models.Model):
    name = models.CharField(max_length=255)
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator(), MinLengthValidator(3, "Username must be at least 3 characters long")],
    )
    profile_picture = models.ImageField(upload_to="organization_profile_pictures/", blank=True)
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True, null=True)
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organizations")
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        add_profile_picture(self)
        super().save(*args, **kwargs)

    @classmethod
    def get_all_organizations(cls):
        """Return all organizations"""
        return cls.objects.all()

    @classmethod
    def get_organizations_by_owner(cls, user):
        """Return all organizations owned by a specific user"""
        return cls.objects.filter(owner=user)

    @classmethod
    def get_organization_by_id(cls, _id):
        return cls.objects.filter(id=_id)
