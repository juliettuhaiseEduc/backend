from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_user_profile_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar_url',
            field=models.URLField(max_length=500, blank=True, default=''),
        ),
    ]
