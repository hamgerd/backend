from django.db.models.enums import TextChoices


class TicketStatusChoice(TextChoices):
    PENDING = "p", "pending"
    SUCCESS = "s", "success"
    CANCELLED = "c", "cancelled"
    EXPIRED = "e", "expired"
