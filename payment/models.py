from django.db import models
from enum import Enum
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone

from config.settings.base import AUTH_USER_MODEL
from organization.models import Organization


class BillStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]


class Bill(models.Model):
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

class TicketBill(Bill):
    status = models.CharField(max_length=20, choices=BillStatus.choices(), default=BillStatus.PENDING.name)
    paid_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)



class Payment(models.Model):
    bill = models.ForeignKey(TicketBill, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    paid_at = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True, null=True)

    def clean(self):
        if self.amount > self.bill.amount:
            raise ValidationError("Payment amount cannot exceed bill amount.")