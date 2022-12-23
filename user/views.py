from django.contrib.auth.hashers import make_password
from django.http import Http404

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

from user.decorators import allowed_role
from user.models import User
from user.serializers import UserSerializer, UserDepositSerializer


class UserLoginView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token, created = Token.objects.get_or_create(user=serializer.validated_data['user'])  # no duplicate sessions
        response = {'token': token.key}
        if not created:
            response.update({'message': 'There is already an active session using your account. '
                                        'You can terminate all active sessions with /logout/all'})
            return Response(response)
        return Response(response)


class UserLogoutView(APIView):

    def get(self, request, format=None):
        sessions_terminated = len(Token.objects.filter(user=request.user).delete())
        return Response({'message': f'User logged out. Sessions terminated: {sessions_terminated}'})


class UserCreateView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response({
                'message': f'{user} successfully created.',
                'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserListApiView(APIView):
#
#     def get(self, request, format=None):
#         serializer = UserSerializer(User.objects.all(), many=True)
#         return Response(serializer.data)


class UserDetailView(APIView):

    def get_object(self, pk, owner=None):
        try:
            user = User.objects.get(pk=pk)
            if owner is None:
                return user
            if user.pk == owner.pk:
                return user
            raise APIException('Cannot edit users except you.')
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user, context={'request': request})
        return Response({'data': serializer.data})

    def put(self, request, pk, format=None):
        user = self.get_object(pk, owner=request.user)
        # password change
        if password := request.data.pop('password', None):
            request.data['password'] = make_password(password)
        # password change
        serializer = UserSerializer(user, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'User successfully updated.',
                             'data': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk, owner=request.user)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserDepositView(APIView):

    @allowed_role(User.Role.BUYER)
    def post(self, request, format=None):
        serializer = UserDepositSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user, amount = request.user, serializer.validated_data['amount']
            user.deposit += amount
            user.save()
            return Response({'message': f'{amount} successfully deposited. {user.deposit} in total.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserResetView(APIView):

    @allowed_role(User.Role.BUYER)
    def post(self, request, format=None):
        user = request.user
        user.deposit = 0
        user.save()
        return Response({'message': f'{user} deposit reset to 0.'})