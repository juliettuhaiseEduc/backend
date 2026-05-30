# Generated manually to add performance indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_admin_weather_location'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='sensorreading',
            index=models.Index(fields=['device', '-recorded_at'], name='device_recorded_at_idx'),
        ),
        migrations.AlterField(
            model_name='sensorreading',
            name='recorded_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
