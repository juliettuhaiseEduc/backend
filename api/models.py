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
    updated_at            = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.email} — {self.plant_type or "No plant set"}'


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
