from datetime import timedelta

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel

from ..events.choices import TicketStatusChoice
from ..organizations.models import Organization
from .choices import AccountingServiceTypeChoice, BillStatusChoice, CommissionActionTypeChoice
from .managers import CommissionRulesManager


class TicketTransaction(BaseModel):
    amount = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)])
    authority = models.CharField(null=True, max_length=128)
    status = models.CharField(max_length=20, choices=BillStatusChoice.choices, default=BillStatusChoice.PENDING.value)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(default=timezone.now, null=True)
    transaction_id = models.CharField(null=True, max_length=128)

    def __str__(self):
        return f"Transaction {self.id}/{self.public_id} - {self.amount}"

    @property
    def expires_at(self):
        return self.created_at + timedelta(minutes=15)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def cancel(self):
        self.status = BillStatusChoice.CANCELLED
        self.tickets.update(status=TicketStatusChoice.CANCELLED)
        self.save()

    def confirm(self, ref_id):
        self.transaction_id = ref_id
        self.status = BillStatusChoice.SUCCESS
        self.tickets.update(status=TicketStatusChoice.SUCCESS)
        self.save()


class CommissionRules(BaseModel):
    start = models.DecimalField(max_digits=12, decimal_places=0)
    end = models.DecimalField(max_digits=12, decimal_places=0)
    action = models.CharField(max_length=3, choices=CommissionActionTypeChoice.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=0)

    objects = CommissionRulesManager()


class OrganizationAccounting(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="accounts")
    service = models.CharField(max_length=20, choices=AccountingServiceTypeChoice.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    extra_arguments = models.JSONField(blank=True, default={})
