from django.contrib import admin
from .models import DailyAgriLog

@admin.register(DailyAgriLog)
class DailyAgriLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'season', 'avg_temp', 'avg_moisture', 'total_rain_mm', 'water_used_l']
    list_filter  = ['season']
    ordering     = ['-date']
