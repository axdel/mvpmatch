from rest_framework import serializers

from product.models import Product


class ProductSerializer(serializers.ModelSerializer):

    seller_id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Product
        fields = ('id', 'product_name', 'seller_id', 'cost', 'amount_available')
        read_only_fields = ('seller_id',)