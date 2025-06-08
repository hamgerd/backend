from django.db.models.enums import TextChoices


class BillStatusChoice(TextChoices):
    PENDING = "p", "pending"
    SUCCESS = "s", "success"
    CANCELLED = "c", "cancelled"


class CurrencyChoice(TextChoices):
    IRR = "IRR", "IRR"
    IRT = "IRT", "IRT"
