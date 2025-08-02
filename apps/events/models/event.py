from django.db import models
from django.utils import timezone
from rest_framework.exceptions import NotAcceptable, ValidationError

from apps.core.models import BaseModel
from apps.organizations.models import Organization

from ..choices import CommissionPayerChoice, EventStatusChoice
from ..validators import geo_location_validator


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
    location = models.CharField(blank=True, max_length=255)  # add blank=True
    geo_location = models.JSONField(null=True, blank=True, validators=[geo_location_validator])
    is_active = models.BooleanField(default=True)
    commission_payer = models.CharField(
        max_length=3, choices=CommissionPayerChoice.choices, default=CommissionPayerChoice.SELLER
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=EventStatusChoice.choices, default=EventStatusChoice.DRAFT.value)
    registration_opening = models.DateTimeField(blank=True, null=True)
    registration_deadline = models.DateTimeField(blank=True, null=True)
    # TODO: AB external_url for redirecting to user landing page
    # TODO: AE add faq field to get and return json

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

    def is_open_to_register(self):
        """
        Returns True if registration is currently open for the event.

        Registration is considered open if:
          - The event status is SCHEDULED.
          - The current datetime falls between the registration opening and deadline windows.
          - If opening or deadline are not set, fallbacks to event's start and end dates.
        """
        if self.status == EventStatusChoice.SCHEDULED:
            now = timezone.now()
            opening = self.registration_opening or self.created_at
            deadline = self.registration_deadline or self.end_date
            if opening and deadline and opening <= now <= deadline:
                return True
        return False

    def clean(self):
        if self.registration_opening:
            if not self.registration_opening < self.start_date:
                raise ValidationError("Registration opening must be before the event start date.")
        if self.registration_deadline:
            if self.registration_deadline > self.end_date:
                raise ValidationError()

    def save(self, *args, **kwargs):
        self.clean()
        if self.pk:  # the object exists, so it's an update
            old = self.__class__.objects.get(pk=self.pk)
            if old.status == EventStatusChoice.COMPLETED.value:
                raise NotAcceptable("Event is already completed.")
        self.full_clean()
        super().save(*args, **kwargs)
