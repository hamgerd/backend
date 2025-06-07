from datetime import timedelta

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel

from ..events.utils import TicketStatus
from .utils import BillStatus


class TicketTransaction(BaseModel):
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    authority = models.CharField(null=True, max_length=128)
    status = models.CharField(max_length=20, choices=BillStatus.choices(), default=BillStatus.PENDING.name)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(default=timezone.now, null=True)
    transaction_id = models.CharField(null=True, max_length=128)

    @property
    def expires_at(self):
        return self.created_at + timedelta(minutes=15)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def cancel(self):
        self.status = BillStatus.CANCELLED
        self.tickets.status = TicketStatus.CANCELLED
        self.save()

    def confirm(self, ref_id):
        self.transaction_id = ref_id
        self.status = BillStatus.CONFIRMED
        self.tickets.status = TicketStatus.CONFIRMED
        self.save()
