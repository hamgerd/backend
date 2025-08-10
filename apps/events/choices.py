from django.db.models.enums import TextChoices


class EventStatusChoice(TextChoices):
    DRAFT = "drf", "Draft"
    PAUSED = "psd", "Paused"
    CANCELED = "cnl", "Canceled"
    SCHEDULED = "sch", "Scheduled"
    COMPLETED = "cpl", "Completed"


class TicketStatusChoice(TextChoices):
    PENDING = "p", "pending"
    SUCCESS = "s", "success"
    CANCELLED = "c", "cancelled"
    EXPIRED = "e", "expired"
