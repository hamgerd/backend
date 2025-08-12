from decimal import Decimal

import pytest
from faker import Faker

from apps.payment.choices import BillStatusChoice, CommissionActionTypeChoice
from apps.payment.models import CommissionRules, TicketTransaction

faker = Faker()


@pytest.fixture
def create_transaction(db):
    def _create_transaction(amount: int | Decimal, status: BillStatusChoice, transaction_id: str):
        return TicketTransaction.objects.create(
            amount=amount, authority=faker.password(length=10), status=status, transaction_id=transaction_id
        )

    return _create_transaction


@pytest.fixture
def create_commission_rule(db):
    def _create_commission_rule(
        start: int | Decimal, end: int | Decimal, action: CommissionActionTypeChoice, amount: int | Decimal
    ):
        return CommissionRules.objects.create(start=start, end=end, action=action, amount=amount)

    return _create_commission_rule
