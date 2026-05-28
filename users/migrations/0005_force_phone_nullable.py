from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_fix_phone_nullable'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE users_user ALTER COLUMN phone_number DROP NOT NULL;',
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
