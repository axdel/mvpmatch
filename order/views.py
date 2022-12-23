from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from user.decorators import allowed_role

from order.serializers import OrderSerializer
from user.models import User


class OrderView(APIView):

    @allowed_role(User.Role.BUYER)
    def post(self, request, format=None):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            with transaction.atomic():
                order = serializer.save()
                order.user_id.deposit -= order.spent
                order.user_id.save()
                order.product_id.amount_available -= order.amount
                order.product_id.save()
            return Response({
                'message': 'Order successfully created.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)