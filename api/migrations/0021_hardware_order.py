from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_add_hardware_order'),
    ]

    operations = [
        # Safe: creates the table only if it doesn't already exist.
        # Handles the case where the broken 0020 partially created it on Railway.
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS api_hardwareorder (
                    id          BIGSERIAL PRIMARY KEY,
                    name        VARCHAR(150) NOT NULL,
                    phone       VARCHAR(20)  NOT NULL,
                    email       VARCHAR(254) NOT NULL DEFAULT '',
                    location    VARCHAR(255) NOT NULL DEFAULT '',
                    kit_type    VARCHAR(20)  NOT NULL,
                    quantity    INTEGER      NOT NULL DEFAULT 1,
                    total_ugx   INTEGER      NOT NULL,
                    notes       TEXT         NOT NULL DEFAULT '',
                    status      VARCHAR(20)  NOT NULL DEFAULT 'pending',
                    created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );
            """,
            reverse_sql="DROP TABLE IF EXISTS api_hardwareorder;",
        ),
        # Tell Django's migration state about the model so ORM works correctly.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='HardwareOrder',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=150)),
                        ('phone', models.CharField(max_length=20)),
                        ('email', models.CharField(blank=True, max_length=254)),
                        ('location', models.CharField(blank=True, max_length=255)),
                        ('kit_type', models.CharField(
                            choices=[
                                ('basic', 'Basic Kit \u2014 UGX 500,000'),
                                ('advanced', 'Advanced Kit \u2014 UGX 2,000,000'),
                            ],
                            max_length=20,
                        )),
                        ('quantity', models.PositiveIntegerField(default=1)),
                        ('total_ugx', models.PositiveIntegerField()),
                        ('notes', models.TextField(blank=True)),
                        ('status', models.CharField(
                            choices=[
                                ('pending', 'Pending'), ('confirmed', 'Confirmed'),
                                ('shipped', 'Shipped'), ('delivered', 'Delivered'),
                                ('cancelled', 'Cancelled'),
                            ],
                            default='pending', max_length=20,
                        )),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                    ],
                    options={'ordering': ['-created_at']},
                ),
            ],
            database_operations=[],  # DB already handled by RunSQL above
        ),
    ]
