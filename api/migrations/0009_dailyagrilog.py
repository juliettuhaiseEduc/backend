from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_add_online_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyAgriLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('season', models.CharField(blank=True, max_length=30)),
                ('avg_temp', models.FloatField(blank=True, null=True)),
                ('avg_moisture', models.FloatField(blank=True, null=True)),
                ('total_rain_mm', models.FloatField(default=0.0)),
                ('water_used_l', models.FloatField(default=0.0)),
                ('rain_prob', models.FloatField(default=0.0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agri_logs', to='users.user')),
            ],
            options={
                'ordering': ['-date'],
                'unique_together': {('user', 'date')},
            },
        ),
    ]
