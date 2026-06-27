import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_pushsubscription'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SMSSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sms_enabled',           models.BooleanField(default=False)),
                ('pump_alerts',           models.BooleanField(default=True)),
                ('weather_alerts',        models.BooleanField(default=True)),
                ('low_water_alerts',      models.BooleanField(default=True)),
                ('sensor_failure_alerts', models.BooleanField(default=True)),
                ('phone_numbers',         models.JSONField(default=list)),
                ('updated_at',            models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sms_settings',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'verbose_name': 'SMS Settings'},
        ),
    ]
