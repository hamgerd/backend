from django.db import models
from enum import Enum
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.events.models import Ticket
from config.settings.base import AUTH_USER_MODEL

from .utils import CurrencyEnum

class BillStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]


class TicketTransaction(models.Model):
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3,choices=CurrencyEnum.choices())
    authority = models.CharField(null=True, max_length=128)
    status = models.CharField(max_length=20, choices=BillStatus.choices(), default=BillStatus.PENDING.name)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(default=timezone.now)
    transaction_id = models.CharField(null=True, max_length=128)
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE,related_name="transactions", null=True)


    def clean(self):
        if self.amount > self.bill.amount:
            raise ValidationError("Payment amount cannot exceed bill amount.")