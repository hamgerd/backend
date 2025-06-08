from django.conf import settings
from django.core import validators
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.core.models import BaseModel
from apps.payment.models import TicketTransaction

from ..choices import TicketStatusChoice
from .event import Event


class TicketType(BaseModel):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    max_participants = models.PositiveIntegerField(validators=[validators.MinValueValidator(1)], null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="ticket_types")
    price = models.PositiveIntegerField()
    # currency = models.CharField(max_length=3, choices=CurrencyEnum.choices())

    @property
    def remaining_tickets(self):
        unavailable_tickets_count = self.tickets.filter(
            status__in=[TicketStatusChoice.SUCCESS.value, TicketStatusChoice.PENDING.value]
        ).count()
        return self.max_participants - unavailable_tickets_count


class Ticket(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name="tickets")
    status = models.CharField(
        max_length=20, choices=TicketStatusChoice.choices, default=TicketStatusChoice.PENDING.value
    )
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

    def clean(self):
        """Validate ticket data"""
        event = self.ticket_type.event

        if event.start_date < timezone.now():
            raise ValidationError("Cannot create ticket for past events.")

        if event.max_participants:
            if self.ticket_type.remaining_tickets < 1:
                raise ValidationError("Event has reached maximum participants.")

    def save(self, *args, **kwargs):
        self.ticket_number = self.ticket_type.tickets.filter(status=TicketStatusChoice.SUCCESS).count() + 1
        self.full_clean()
        super().save(*args, **kwargs)

    def confirm(self):
        """Confirm the ticket"""
        if self.status == TicketStatusChoice.PENDING.value:
            self.status = TicketStatusChoice.SUCCESS.value
            self.save()
            return True
        return False

    def cancel(self):
        """Cancel the ticket"""
        if self.status in [TicketStatusChoice.PENDING.value, TicketStatusChoice.SUCCESS.value]:
            self.status = TicketStatusChoice.CANCELLED.value
            self.save()
            return True
        return False
