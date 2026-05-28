from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_fix_email_nullable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
