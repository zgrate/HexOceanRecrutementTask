from django.core.exceptions import ValidationError


def is_above_zero(value):
    if value <= 0:
        raise ValidationError(f"{value} is smaller or equal 0")


def is_above_or_equal_zero(value):
    if value < 0:
        raise ValidationError(f"{value} is smaller then 0")
