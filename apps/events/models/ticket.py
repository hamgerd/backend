from django.apps import apps
from django.conf import settings
from django.core import validators
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.core.models import BaseModel

from ...payment.models import TicketTransaction
from ...payment.utils import BillStatus
from ..utils import TicketStatus
from .event import Event


class TicketType(BaseModel):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    max_participants = models.PositiveIntegerField(validators=[validators.MinValueValidator(1)], null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="ticket_types")
    price = models.PositiveIntegerField()
    # currency = models.CharField(max_length=3, choices=CurrencyEnum.choices())


class Ticket(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name="tickets")
    status = models.CharField(max_length=20, choices=TicketStatus.choices(), default=TicketStatus.PENDING.value)
    ticket_number = models.PositiveSmallIntegerField(editable=False)
    final_amount = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction = models.ForeignKey(
        TicketTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"

    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.event.title}"

    @property
    def remaining_tickets(self):
        event = self.ticket_type.event

        confirmed_count = (
            self.ticket_type.tickets.filter(status=TicketStatus.CONFIRMED.value).exclude(id=self.id).count()
        )

        # Pending transactions excluding this one (if it exists)
        TicketTransaction = apps.get_model("payment", "TicketTransaction")
        pending_count = (
            TicketTransaction.objects.filter(ticket__ticket_type__event=event, status=BillStatus.PENDING.name)
            .exclude(ticket_id=self.id)
            .count()
        )

        return confirmed_count + pending_count

    def clean(self):
        """Validate ticket data"""
        event = self.ticket_type.event

        if event.start_date < timezone.now():
            raise ValidationError("Cannot create ticket for past events.")

        if event.max_participants:
            # Confirmed tickets excluding this one
            if self.remaining_tickets >= event.max_participants:
                raise ValidationError("Event has reached maximum participants.")

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
