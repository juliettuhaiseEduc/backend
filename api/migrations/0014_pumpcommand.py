# Generated manually to add PumpCommand model

from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_add_sensorreading_indexes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PumpCommand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('command', models.CharField(choices=[('On', 'On'), ('Off', 'Off')], max_length=10)),
                ('issued_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pump_commands', to='api.device')),
                ('issued_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pump_commands', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-issued_at'],
            },
        ),
        migrations.AddIndex(
            model_name='pumpcommand',
            index=models.Index(fields=['device', '-issued_at'], name='pump_cmd_device_time_idx'),
        ),
    ]
