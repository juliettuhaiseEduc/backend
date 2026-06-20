from django.contrib import admin
from .models import DailyAgriLog, Device

@admin.register(DailyAgriLog)
class DailyAgriLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'season', 'avg_temp', 'avg_moisture', 'total_rain_mm', 'water_used_l']
    list_filter  = ['season']
    ordering     = ['-date']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display  = ['device_id', 'device_name', 'user', 'secret_key', 'pairing_code', 'status', 'is_paired', 'created_at']
    search_fields = ['device_id', 'device_name', 'secret_key']
    readonly_fields = ['device_id', 'secret_key', 'pairing_code', 'created_at', 'paired_at']
    ordering      = ['-created_at']
