from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_add_hardware_order'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Safe: creates the table only if it doesn't already exist.
        # The original 0020 may have created it on some environments.
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS api_systemsettings (
                    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                    system_online       BOOLEAN NOT NULL DEFAULT 1,
                    maintenance_title   VARCHAR(200) NOT NULL DEFAULT 'System Maintenance',
                    maintenance_message TEXT NOT NULL DEFAULT 'The system is currently under maintenance. Please check back later.',
                    maintenance_sub     VARCHAR(300) NOT NULL DEFAULT 'We apologize for the inconvenience.',
                    online_at           DATETIME NULL,
                    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_by_id       INTEGER NULL REFERENCES users_user(id) ON DELETE SET NULL
                );
            """,
            reverse_sql="DROP TABLE IF EXISTS api_systemsettings;",
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='SystemSettings',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('system_online', models.BooleanField(default=True)),
                        ('maintenance_title', models.CharField(default='System Maintenance', max_length=200)),
                        ('maintenance_message', models.TextField(default='The system is currently under maintenance. Please check back later.')),
                        ('maintenance_sub', models.CharField(blank=True, default='We apologize for the inconvenience.', max_length=300)),
                        ('online_at', models.DateTimeField(blank=True, help_text='Scheduled time to go back online', null=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={'verbose_name': 'System Settings'},
                ),
            ],
            database_operations=[],
        ),
    ]
