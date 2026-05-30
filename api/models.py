from django.db import models
from users.models import User


class Device(models.Model):
    STATUS_CHOICES = [('Online', 'Online'), ('Offline', 'Offline')]

    user              = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id         = models.CharField(max_length=100, unique=True)
    secret_key        = models.CharField(max_length=255)
    device_name       = models.CharField(max_length=150)
    pairing_code      = models.CharField(max_length=20, unique=True)  # e.g., GX92A7
    activation_token  = models.CharField(max_length=50, blank=True)   # Temporary test token
    is_paired         = models.BooleanField(default=False)
    crop_type         = models.CharField(max_length=100, blank=True)
    soil_type         = models.CharField(max_length=100, blank=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Offline')
    last_seen         = models.DateTimeField(null=True, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    paired_at         = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.device_name} ({self.device_id})'


class FarmSettings(models.Model):
    SOIL_CHOICES = [
        ('Sandy',      'Sandy'),
        ('Clay',       'Clay'),
        ('Silt',       'Silt'),
        ('Loam',       'Loam'),
        ('Sandy Loam', 'Sandy Loam'),
        ('Clay Loam',  'Clay Loam'),
        ('Peat',       'Peat'),
        ('Chalk',      'Chalk'),
    ]

    user                  = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farm_settings')
    soil_type             = models.CharField(max_length=50, choices=SOIL_CHOICES, blank=True)
    plant_type            = models.CharField(max_length=100, blank=True)
    moisture_min          = models.FloatField(default=40.0)
    moisture_max          = models.FloatField(default=70.0)
    moisture_critical_low = models.FloatField(default=20.0)
    irrigation_duration   = models.PositiveIntegerField(default=30, help_text='Minutes per irrigation cycle')
    notes                 = models.TextField(blank=True)
    weather_lat           = models.FloatField(null=True, blank=True)
    weather_lon           = models.FloatField(null=True, blank=True)
    weather_location_name = models.CharField(max_length=200, blank=True, default='')
    updated_at            = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.email} — {self.plant_type or "No plant set"}'


class SensorReading(models.Model):
    device     = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    soil_moisture  = models.FloatField(null=True, blank=True)
    temperature    = models.FloatField(null=True, blank=True)
    humidity       = models.FloatField(null=True, blank=True)
    water_tank     = models.FloatField(null=True, blank=True)
    pump_status    = models.CharField(max_length=20, default='Off')
    irrig_cycles   = models.PositiveIntegerField(default=0)
    recorded_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f'{self.device.device_name} @ {self.recorded_at}'


class Notification(models.Model):
    TYPE_CHOICES = [
        ('pump',    'Pump'),
        ('weather', 'Weather'),
        ('water',   'Low Water'),
        ('sensor',  'Sensor Failure'),
        ('system',  'System'),
    ]

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type        = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    title       = models.CharField(max_length=200)
    message     = models.TextField()
    device_name = models.CharField(max_length=150, blank=True)
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.type}] {self.title}'


class WeatherAccessLog(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weather_logs')
    endpoint   = models.CharField(max_length=50, default='weather')
    lat        = models.FloatField(null=True, blank=True)
    lon        = models.FloatField(null=True, blank=True)
    location   = models.CharField(max_length=200, blank=True)
    success    = models.BooleanField(default=True)
    accessed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-accessed_at']

    def __str__(self):
        return f'{self.user} — {self.location} @ {self.accessed_at}'


class DailyAgriLog(models.Model):
    """
    One row per user per day — feeds seasonal learning.
    Written automatically on each weather fetch.
    """
    user          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agri_logs')
    date          = models.DateField()
    season        = models.CharField(max_length=30, blank=True)
    avg_temp      = models.FloatField(null=True, blank=True)
    avg_moisture  = models.FloatField(null=True, blank=True)
    total_rain_mm = models.FloatField(default=0.0)
    water_used_l  = models.FloatField(default=0.0)
    rain_prob     = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f'{self.user} — {self.date} ({self.season})'


class LocationCache(models.Model):
    search_term  = models.CharField(max_length=255, unique=True, db_index=True)
    display_name = models.TextField()
    latitude     = models.FloatField()
    longitude    = models.FloatField()
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Location Cache'

    def __str__(self):
        return f'{self.search_term} → {self.display_name}'


class SystemSettings(models.Model):
    """Singleton — only one row ever exists (pk=1)"""
    system_online        = models.BooleanField(default=True)
    maintenance_title    = models.CharField(max_length=200, default='System Maintenance')
    maintenance_message  = models.TextField(default='The system is currently under maintenance. Please check back later.')
    maintenance_sub      = models.CharField(max_length=300, blank=True, default='We apologize for the inconvenience.')
    online_at            = models.DateTimeField(null=True, blank=True, help_text='Scheduled time to go back online')
    updated_at           = models.DateTimeField(auto_now=True)
    updated_by           = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    class Meta:
        verbose_name = 'System Settings'

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f'System {"Online" if self.system_online else "Offline"}'
