from django.http import Http404
from rest_framework.exceptions import APIException

from product.models import Product
from product.serializers import ProductSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from user.decorators import allowed_role
from user.models import User


class ProductListView(APIView):

    def get(self, request, format=None):
        serializer = ProductSerializer(Product.objects.all(), many=True)
        return Response(serializer.data)

    @allowed_role(User.Role.SELLER)
    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):

    def get_object(self, pk, owner=None):
        try:
            product = Product.objects.get(pk=pk)
            if owner is None:
                return product
            if product.is_owned_by(owner):
                return product
            raise APIException('Cannot edit products you do not own.')
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)

    @allowed_role(User.Role.SELLER)
    def put(self, request, pk, format=None):
        product = self.get_object(pk, owner=request.user)
        serializer = ProductSerializer(product, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': f'Product {product.product_name} updated', 'data': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @allowed_role(User.Role.SELLER)
    def delete(self, request, pk, format=None):
        product = self.get_object(pk, owner=request.user)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)