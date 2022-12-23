from django.contrib import admin
from django.urls import path, include

from order.views import OrderView
from user.views import UserLoginView, UserLogoutView, UserDepositView, UserResetView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    path('login', UserLoginView.as_view(), name='login'),
    path('logout', UserLogoutView.as_view(), name='logout'),
    path('logout/all', UserLogoutView.as_view(), name='logout_all'),

    path('products/', include('product.urls')),
    path('users/', include('user.urls')),

    path('deposit', UserDepositView.as_view(), name='user_deposit'),
    path('buy', OrderView.as_view(), name='order'),
    path('reset', UserResetView.as_view(), name='user_deposit_reset'),
]
