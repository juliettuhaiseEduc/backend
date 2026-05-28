from django.urls import path
from .views import SignupView, LoginView, CheckIdentifierView
from .admin_views import (
    AdminUserListView, AdminUserDetailView,
    AdminDeviceListView, AdminDeviceDetailView,
)

urlpatterns = [
    path('signup/',                    SignupView.as_view(),            name='signup'),
    path('login/',                     LoginView.as_view(),             name='login'),
    path('check-identifier/',          CheckIdentifierView.as_view(),  name='check-identifier'),
    path('admin/users/',               AdminUserListView.as_view(),    name='admin-users'),
    path('admin/users/<int:pk>/',      AdminUserDetailView.as_view(),  name='admin-user-detail'),
    path('admin/devices/',             AdminDeviceListView.as_view(),  name='admin-devices'),
    path('admin/devices/<int:pk>/',    AdminDeviceDetailView.as_view(), name='admin-device-detail'),
]
