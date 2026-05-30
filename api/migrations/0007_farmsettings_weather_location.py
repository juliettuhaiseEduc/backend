from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_weatheraccesslog'),
    ]

    operations = [
        migrations.AddField(
            model_name='farmsettings',
            name='weather_lat',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='farmsettings',
            name='weather_lon',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='farmsettings',
            name='weather_location_name',
            field=models.CharField(max_length=200, blank=True, default=''),
        ),
    ]
