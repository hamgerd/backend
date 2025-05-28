from enum import Enum

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.organizations.models import Organization
from config.settings.base import AUTH_USER_MODEL


class TicketStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

    @classmethod
    def choices(cls):
        return [(status.value, status.name.title()) for status in cls]


class EventCategory(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Event Category"
        verbose_name_plural = "Event Categories"

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="events")
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE, related_name="events", null=True, blank=True)
    image = models.ImageField(upload_to="events/images/", null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255)
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
    def max_participants(self):
        return sum([item.max_participants for item in self.ticket_types.all()])


class TicketType(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    max_participants = models.PositiveIntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="ticket_types")
    price = models.PositiveIntegerField()


class Ticket(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name="tickets")
    status = models.CharField(max_length=20, choices=TicketStatus.choices(), default=TicketStatus.PENDING.value)
    ticket_number = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        unique_together = ["user", "ticket_type"]

    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.event.title}"

    def clean(self):
        """Validate ticket data"""
        if self.event.start_date < timezone.now():
            raise ValidationError("Cannot create ticket for past events")

        if self.event.max_participants:
            confirmed_tickets = (
                self.event.tickets.filter(status=TicketStatus.CONFIRMED.value).exclude(id=self.id).count()
            )
            if confirmed_tickets >= self.event.max_participants:
                raise ValidationError("Event has reached maximum participants")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def confirm(self):
        """Confirm the ticket"""
        if self.status == TicketStatus.PENDING.value:
            self.status = TicketStatus.CONFIRMED.value
            self.save()
            return True
        return False

    def cancel(self):
        """Cancel the ticket"""
        if self.status in [TicketStatus.PENDING.value, TicketStatus.CONFIRMED.value]:
            self.status = TicketStatus.CANCELLED.value
            self.save()
            return True
        return False

    def is_valid(self):
        """Check if ticket is valid"""
        if self.status != TicketStatus.CONFIRMED.value:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            self.status = TicketStatus.EXPIRED.value
            self.save()
            return False
        return True

    @classmethod
    def get_user_tickets(cls, user):
        """Get all tickets for a user"""
        return cls.objects.filter(user=user)

    @classmethod
    def get_event_tickets(cls, event):
        """Get all tickets for an event"""
        return cls.objects.filter(event=event)

    @property
    def event(self):
        return self.ticket_type.event
