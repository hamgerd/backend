from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel
from apps.organizations.models import Organization


class EventCategory(BaseModel):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Event Category"
        verbose_name_plural = "Event Categories"

    def __str__(self):
        return self.title


class Event(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="events")
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE, related_name="events", null=True, blank=True)
    image = models.ImageField(upload_to="events/images/", null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return f"{self.title} - {self.organization.name}"

    @classmethod
    def get_all_events(cls):
        """Return all active events"""
        return cls.objects.filter(is_active=True)

    @classmethod
    def get_events_by_organization(cls, organization_id):
        """Return all events for a specific organization"""
        return cls.objects.filter(organization_id=organization_id, is_active=True)

    @classmethod
    def get_featured_events(cls):
        """Return all featured events"""
        return cls.objects.filter(is_active=True, start_date__gte=timezone.now())[:10]

    @property
    def max_participants(self) -> int:
        return sum([item.max_participants for item in self.ticket_types.all()])
