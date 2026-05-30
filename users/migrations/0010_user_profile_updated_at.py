from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_add_last_seen'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
