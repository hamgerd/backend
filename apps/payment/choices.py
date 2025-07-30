from django.db.models.enums import TextChoices


class BillStatusChoice(TextChoices):
    PENDING = "p", "pending"
    SUCCESS = "s", "success"
    CANCELLED = "c", "cancelled"


class CurrencyChoice(TextChoices):
    IRR = "IRR", "IRR"
    IRT = "IRT", "IRT"


class CommissionActionTypeChoice(TextChoices):
    PERCENTAGE = "p", "percentage"
    CONSTANT = "c", "constant"


class AccountingServiceTypeChoice(TextChoices):
    EVENT_PAYMENT = "eventpayment", "event payment"


class BalanceTypeChoice(TextChoices):
    DEBIT = "dbt", "Debit"
    CREDIT = "crd", "Credit"
