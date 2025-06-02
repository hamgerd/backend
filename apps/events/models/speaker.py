from django.db import models

from ...core.utils.identicon import add_default_image
from apps.core.models import BaseModel
from .event import Event


class Speaker(BaseModel):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="speakers/images/", blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="speakers")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.image:
            add_default_image(self, username_field_name="name")
        super().save(*args, **kwargs)
