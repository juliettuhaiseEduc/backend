from django.urls import path
from .views import SignupView, LoginView, CheckIdentifierView
from .admin_views import (
    AdminUserListView, AdminUserDetailView,
    AdminDeviceListView, AdminDeviceDetailView,
    AdminGenerateDeviceView, AdminDeviceStatsView, AdminDeviceFixView,
    AdminWeatherView,
)

urlpatterns = [
    path('signup/',                         SignupView.as_view(),             name='signup'),
    path('login/',                          LoginView.as_view(),              name='login'),
    path('check-identifier/',               CheckIdentifierView.as_view(),   name='check-identifier'),
    path('admin/users/',                    AdminUserListView.as_view(),      name='admin-users'),
    path('admin/users/<int:pk>/',           AdminUserDetailView.as_view(),    name='admin-user-detail'),
    path('admin/devices/',                  AdminDeviceListView.as_view(),    name='admin-devices'),
    path('admin/devices/generate/',         AdminGenerateDeviceView.as_view(),name='admin-device-generate'),
    path('admin/devices/<int:pk>/',         AdminDeviceDetailView.as_view(),  name='admin-device-detail'),
    path('admin/devices/<int:pk>/stats/',   AdminDeviceStatsView.as_view(),   name='admin-device-stats'),
    path('admin/devices/<int:pk>/fix/',     AdminDeviceFixView.as_view(),     name='admin-device-fix'),
    path('admin/weather/',                  AdminWeatherView.as_view(),       name='admin-weather'),
]
