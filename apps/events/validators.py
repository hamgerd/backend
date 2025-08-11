from django.core.exceptions import ValidationError


def zero_or_greater_than_1000(value):
    if value != 0 and value < 1000:
        raise ValidationError("Value must be 0 or greater than or equal to 1000")
    return None
