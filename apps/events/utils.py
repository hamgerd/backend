from enum import Enum


class TicketStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

    @classmethod
    def choices(cls):
        return [(status.value, status.name.title()) for status in cls]
