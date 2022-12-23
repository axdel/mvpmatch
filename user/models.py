from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Deposit(models.IntegerChoices):
        CENT_5 = 5
        CENT_10 = 10
        CENT_20 = 20
        CENT_50 = 50
        CENT_100 = 100

    class Role(models.TextChoices):
        BUYER = 'buyer'  # can deposit coins into the machine and make purchases
        SELLER = 'seller'  # can add, update or remove products

    deposit = models.PositiveIntegerField(default=0)
    role = models.CharField(max_length=8, choices=Role.choices)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f'{self.username} ({self.role})'