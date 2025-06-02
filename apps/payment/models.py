from datetime import timedelta
from enum import Enum

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel
from apps.events.models import Ticket, TicketStatus
from .utils import CurrencyEnum


class BillStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]


class TicketTransaction(BaseModel):
    # description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, choices=CurrencyEnum.choices())
    authority = models.CharField(null=True, max_length=128)
    status = models.CharField(max_length=20, choices=BillStatus.choices(), default=BillStatus.PENDING.name)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(default=timezone.now, null=True)
    transaction_id = models.CharField(null=True, max_length=128)
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name="transactions", null=True)

    def clean(self):
        if self.amount > self.bill.amount:
            raise ValidationError("Payment amount cannot exceed bill amount.")

    @property
    def expires_at(self):
        return self.created_at + timedelta(minutes=15)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def cancel(self):
        self.status = BillStatus.CANCELLED
        self.ticket.status = TicketStatus.CANCELLED
        self.save()

    def confirm(self):
        self.status = BillStatus.CONFIRMED
        self.ticket.status = TicketStatus.CONFIRMED
        self.save()
