from rest_framework import serializers

from product.serializers import ProductSerializer
from order.serializers import OrderSerializer
from user.models import User


class UserSerializer(serializers.ModelSerializer):

    products = ProductSerializer(read_only=True, many=True)
    orders = OrderSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'role', 'deposit', 'products', 'orders')
        read_only_fields = ('deposit', 'products', 'orders')
        extra_kwargs = {'password': {'write_only': True}}


class UserDepositSerializer(serializers.Serializer):

    amount = serializers.IntegerField()

    def validate_amount(self, amount):
        if amount not in User.Deposit.values:
            raise serializers.ValidationError(f'Amount must be one of {User.Deposit.values}.')
        return amount