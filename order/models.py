from collections import defaultdict
from math import floor

from django.db import models

from user.models import User


class Order(models.Model):

    user_id = models.ForeignKey('user.User', on_delete=models.PROTECT, related_name='orders')
    product_id = models.ForeignKey('product.Product', on_delete=models.PROTECT, related_name='orders')
    amount = models.PositiveIntegerField()
    spent = models.PositiveIntegerField()
    change = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f'Order(user={self.user_id}, product={self.product_id}, amount={self.amount})'

    @property
    def change_in_coins(self):
        '''
        https://everydaycalculation.com/cash-denomination-calculator.php
        divide the amount with the highest denomination. the quotient is the number of notes required for that denomination.
        use the remainder as the dividend for division by the next highest denomination and so on until all denominations are covered.
        '''
        change = self.change
        change_in_coins = defaultdict(int)
        for coin_value in sorted(User.Deposit.values, reverse=True):
            change_in_coins[coin_value] = floor(change / coin_value)
            change %= coin_value
        return list(reversed(change_in_coins.values()))  # array of 5, 10, 20, 50 and 100 cent coins