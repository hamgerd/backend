from django.db import models
from django.core.validators import MinValueValidator
from organization.models import Organization

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='events'
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    max_participants = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return f"{self.title} - {self.organization.name}"

    @classmethod
    def get_all_events(cls):
        """Return all active events"""
        return cls.objects.filter(is_active=True)

    @classmethod
    def get_events_by_organization(cls, organization_id):
        """Return all events for a specific organization"""
        return cls.objects.filter(
            organization_id=organization_id,
            is_active=True
        )

