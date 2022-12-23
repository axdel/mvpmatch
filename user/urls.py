from django.urls import path

from user.views import UserCreateView, UserDetailView


urlpatterns = [
    path('', UserCreateView.as_view(), name='user_create'),
    path('<int:pk>/', UserDetailView.as_view(), name='user_detail'),
]