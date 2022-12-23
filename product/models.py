from django.db import models

from product.validators import product_cost_validator, product_amount_validator


class Product(models.Model):

    product_name = models.CharField(max_length=255, unique=True)
    cost = models.PositiveIntegerField(validators=[product_cost_validator])  # cost in cents
    amount_available = models.PositiveIntegerField(validators=[product_amount_validator])
    seller_id = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='products')

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    # if using Django permissions
    # class Meta:
    #     permissions = [
    #         ('buyer', 'Can deposit coins into the machine and make purchases'),
    #         ('seller', 'Can add, update or remove products'),
    #     ]

    def __str__(self):
        return self.product_name

    def is_owned_by(self, owner):
        return bool(self.seller_id == owner)