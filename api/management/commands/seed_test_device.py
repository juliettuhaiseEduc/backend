from django.core.management.base import BaseCommand, CommandError
from api.models import Device
from users.models import User


class Command(BaseCommand):
    help = 'Seed a test device for a specific user (multi-tenant safe)'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Email of the user to assign the device to')

    def handle(self, *args, **kwargs):
        email = kwargs['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CommandError(f'No user found with email: {email}')

        device, created = Device.objects.get_or_create(
            device_id='EDF-IRR-1024',
            defaults={
                'user':             user,
                'secret_key':       'dev-secret-key',
                'device_name':      'Test Irrigation Device',
                'pairing_code':     'GX92A7',
                'activation_token': 'TEST-ABC123',
                'is_paired':        False,
                'status':           'Offline',
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(
                f'Test device created for {email}:\n'
                f'  Device ID:    EDF-IRR-1024\n'
                f'  Test Code:    TEST-ABC123\n'
                f'  Pairing Code: GX92A7'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'Test device already exists (owned by {device.user.email}):\n'
                f'  Device ID:    {device.device_id}\n'
                f'  Test Code:    {device.activation_token}\n'
                f'  Pairing Code: {device.pairing_code}'
            ))
