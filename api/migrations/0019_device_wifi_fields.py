from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_add_phones_dirty'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='wifi_ssid',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AddField(
            model_name='device',
            name='wifi_password',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AddField(
            model_name='device',
            name='wifi_pending',
            field=models.BooleanField(default=False),
        ),
    ]
