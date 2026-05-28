from django.urls import path
from .views import (
    DeviceListView, DeviceDetailView, ConnectDeviceView,
    DashboardView, HealthCheckView, WeatherView, WeatherLocationView,
    NotificationListView, NotificationDetailView, NotificationMarkAllReadView,
    WifiStatusView, WifiScanView, WifiConfigureView,
    FarmSettingsView, PairDeviceView, TestDeviceView,
    SensorIngestView, LiveDataView, PumpControlView,
)

urlpatterns = [
    path('core/health/',                   HealthCheckView.as_view(),              name='health-check'),
    path('dashboard/',                     DashboardView.as_view(),                name='dashboard'),
    path('weather/',                       WeatherView.as_view(),                  name='weather'),
    path('weather/location/',              WeatherLocationView.as_view(),          name='weather-location'),
    path('devices/',                       DeviceListView.as_view(),               name='device-list'),
    path('devices/<int:pk>/',              DeviceDetailView.as_view(),             name='device-detail'),
    path('device/connect/',                ConnectDeviceView.as_view(),            name='device-connect'),
    path('device/pair/',                   PairDeviceView.as_view(),               name='device-pair'),
    path('device/test/',                   TestDeviceView.as_view(),               name='device-test'),
    path('sensor/ingest/',                 SensorIngestView.as_view(),             name='sensor-ingest'),
    path('live-data/',                     LiveDataView.as_view(),                 name='live-data'),
    path('pump/control/',                  PumpControlView.as_view(),              name='pump-control'),
    path('notifications/',                 NotificationListView.as_view(),         name='notification-list'),
    path('notifications/mark-all-read/',   NotificationMarkAllReadView.as_view(),  name='notification-mark-all'),
    path('notifications/<int:pk>/',        NotificationDetailView.as_view(),       name='notification-detail'),
    path('wifi/status/',                   WifiStatusView.as_view(),               name='wifi-status'),
    path('wifi/scan/',                     WifiScanView.as_view(),                 name='wifi-scan'),
    path('wifi/configure/',                WifiConfigureView.as_view(),            name='wifi-configure'),
    path('farm-settings/',                 FarmSettingsView.as_view(),             name='farm-settings'),
]
