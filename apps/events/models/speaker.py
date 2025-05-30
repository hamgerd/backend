from django.db import models

from .event import Event


class Speaker(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="speakers/images/", blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="speakers")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
