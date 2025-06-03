from enum import Enum

class BillStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]

class CurrencyEnum(Enum):
    IRR = "IRR"
    IRT = "IRT"

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]