from datetime import timedelta

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel

from ..events.choices import TicketStatusChoice
from .choices import BillStatusChoice


class TicketTransaction(BaseModel):
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    authority = models.CharField(null=True, max_length=128)
    status = models.CharField(max_length=20, choices=BillStatusChoice.choices, default=BillStatusChoice.PENDING.name)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(default=timezone.now, null=True)
    transaction_id = models.CharField(null=True, max_length=128)

    def __str__(self):
        return f"Transaction {self.id}/{self.public_id} - {self.amount}"

    @property
    def expires_at(self):
        return self.created_at + timedelta(minutes=15)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def cancel(self):
        self.status = BillStatusChoice.CANCELLED
        self.tickets.status = TicketStatusChoice.CANCELLED
        self.save()

    def confirm(self, ref_id):
        self.transaction_id = ref_id
        self.status = BillStatusChoice.SUCCESS
        self.tickets.status = TicketStatusChoice.SUCCESS
        self.save()
