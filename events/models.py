from time import timezone

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from config.settings.base import AUTH_USER_MODEL
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


class Ticket(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_EXPIRED = 'expired'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_EXPIRED, 'Expired'),
    ]

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    ticket_number = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        unique_together = ['user', 'event']

    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.event.title}"

    def clean(self):
        """Validate ticket data"""
        if self.event.start_date < timezone.now():
            raise ValidationError("Cannot create ticket for past events")
        
        if self.event.max_participants:
            confirmed_tickets = self.event.tickets.filter(
                status=self.STATUS_CONFIRMED
            ).exclude(id=self.id).count()
            if confirmed_tickets >= self.event.max_participants:
                raise ValidationError("Event has reached maximum participants")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def confirm(self):
        """Confirm the ticket"""
        if self.status == self.STATUS_PENDING:
            self.status = self.STATUS_CONFIRMED
            self.save()
            return True
        return False

    def cancel(self):
        """Cancel the ticket"""
        if self.status in [self.STATUS_PENDING, self.STATUS_CONFIRMED]:
            self.status = self.STATUS_CANCELLED
            self.save()
            return True
        return False

    def is_valid(self):
        """Check if ticket is valid"""
        if self.status != self.STATUS_CONFIRMED:    
            return False
        if self.expires_at and self.expires_at < timezone.now():
            self.status = self.STATUS_EXPIRED
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