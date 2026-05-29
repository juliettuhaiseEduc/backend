from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignupView, LoginView, CheckIdentifierView, SetPasswordView, HeartbeatView, MeView
from .admin_views import (
    AdminUserListView, AdminUserDetailView,
    AdminDeviceListView, AdminDeviceDetailView,
    AdminGenerateDeviceView, AdminDeviceStatsView, AdminDeviceFixView,
    AdminWeatherView, AdminSettingsView, SystemStatusView,
)

urlpatterns = [
    path('me/',                              MeView.as_view(),                name='me'),
    path('token/refresh/',                   TokenRefreshView.as_view(),      name='token-refresh'),
    path('signup/',                         SignupView.as_view(),             name='signup'),
    path('login/',                          LoginView.as_view(),              name='login'),
    path('set-password/',                   SetPasswordView.as_view(),        name='set-password'),
    path('heartbeat/',                       HeartbeatView.as_view(),          name='heartbeat'),
    path('check-identifier/',               CheckIdentifierView.as_view(),   name='check-identifier'),
    path('admin/users/',                    AdminUserListView.as_view(),      name='admin-users'),
    path('admin/users/<int:pk>/',           AdminUserDetailView.as_view(),    name='admin-user-detail'),
    path('admin/devices/',                  AdminDeviceListView.as_view(),    name='admin-devices'),
    path('admin/devices/generate/',         AdminGenerateDeviceView.as_view(),name='admin-device-generate'),
    path('admin/devices/<int:pk>/',         AdminDeviceDetailView.as_view(),  name='admin-device-detail'),
    path('admin/devices/<int:pk>/stats/',   AdminDeviceStatsView.as_view(),   name='admin-device-stats'),
    path('admin/devices/<int:pk>/fix/',     AdminDeviceFixView.as_view(),     name='admin-device-fix'),
    path('admin/weather/',                  AdminWeatherView.as_view(),       name='admin-weather'),
    path('admin/settings/',                 AdminSettingsView.as_view(),      name='admin-settings'),
    path('system/status/',                  SystemStatusView.as_view(),       name='system-status'),
]
