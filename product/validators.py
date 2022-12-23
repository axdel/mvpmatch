from django.core.exceptions import ValidationError


def product_amount_validator(amount):
    if amount <= 0:
        raise ValidationError(f'Product amount must be greater than 0.')

def product_cost_validator(cost):
    if cost % 5 != 0:
        raise ValidationError(f'Product cost should be in multiples of 5. Provided: {cost}.')