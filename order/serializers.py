from rest_framework import serializers

from order.models import Order


class OrderSerializer(serializers.ModelSerializer):

    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = ('id', 'user_id', 'product_id', 'amount', 'spent', 'change', 'change_in_coins')
        read_only_fields = ('user_id', 'spent', 'change', 'change_in_coins')

    def validate(self, attrs):
        user, product, amount = attrs['user_id'], attrs['product_id'], attrs['amount']
        if product.amount_available < amount:
            raise serializers.ValidationError(f'Not enough {product} on stock. '
                                              f'{amount} required, only {product.amount_available} available.')
        spent = product.cost * amount
        if spent > user.deposit:
            raise serializers.ValidationError(f'Not enough funds. '
                                              f'{spent}c required, only {user.deposit}c available.')
        change = user.deposit - spent
        attrs['spent'], attrs['change'] = spent, change
        return attrs