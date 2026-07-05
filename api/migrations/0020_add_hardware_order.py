from django.db import migrations


class Migration(migrations.Migration):
    """
    This migration was previously broken (mixed HardwareOrder + SystemSettings fields).
    Replaced with a no-op. The actual HardwareOrder table is created in 0021.
    """
    dependencies = [
        ('api', '0019_device_wifi_fields'),
    ]

    operations = []
