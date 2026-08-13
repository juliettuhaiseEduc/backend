from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Drop and recreate public schema to allow clean migrations'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE;")
            cursor.execute("CREATE SCHEMA public;")
            cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
            cursor.execute("GRANT ALL ON SCHEMA public TO public;")
        self.stdout.write(self.style.SUCCESS('Schema reset successfully'))
