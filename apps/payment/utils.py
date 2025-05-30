from enum import Enum

class CurrencyEnum(Enum):
    IRR = "IRR"
    IRT = "IRT"

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]