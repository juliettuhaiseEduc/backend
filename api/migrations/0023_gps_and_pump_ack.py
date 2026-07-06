from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_system_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensorreading',
            name='gps_lat',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sensorreading',
            name='gps_lon',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sensorreading',
            name='gps_place',
            field=models.CharField(max_length=200, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='pumpcommand',
            name='acknowledged',
            field=models.BooleanField(default=False),
        ),
    ]
