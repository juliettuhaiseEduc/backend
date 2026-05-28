from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_fix_email_nullable'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE users_user ALTER COLUMN phone_number DROP NOT NULL;',
            reverse_sql='ALTER TABLE users_user ALTER COLUMN phone_number SET NOT NULL;',
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
