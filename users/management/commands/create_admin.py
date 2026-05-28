from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Create a superuser admin account'

    def add_arguments(self, parser):
        parser.add_argument('email',    type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('--name',   type=str, default='Admin')

    def handle(self, *args, **kwargs):
        email    = kwargs['email']
        password = kwargs['password']
        name     = kwargs['name']

        if User.objects.filter(email=email).exists():
            self.stdout.write(f'Admin already exists: {email}')
            return

        User.objects.create_superuser(email=email, password=password, full_name=name)
        self.stdout.write(self.style.SUCCESS(f'Superuser created: {email}'))
