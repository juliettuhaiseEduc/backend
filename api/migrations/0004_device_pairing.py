# Generated migration for Device model updates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_farmsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='pairing_code',
            field=models.CharField(max_length=20, unique=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='device',
            name='activation_token',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='device',
            name='is_paired',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='device',
            name='paired_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
