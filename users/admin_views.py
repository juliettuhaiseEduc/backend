import uuid
import secrets
import string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User
from api.models import Device, SensorReading, FarmSettings


class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by('-id')
        data = []
        for u in users:
            fs = FarmSettings.objects.filter(user=u).first()
            data.append({
                'id':           u.id,
                'full_name':    u.full_name,
                'email':        u.email,
                'phone_number': u.phone_number,
                'is_staff':     u.is_staff,
                'is_active':    u.is_active,
                'created_at':   u.created_at,
                'device_count': u.devices.count(),
                'soil_type':    fs.soil_type    if fs else '',
                'plant_type':   fs.plant_type   if fs else '',
                'moisture_min': fs.moisture_min if fs else None,
                'moisture_max': fs.moisture_max if fs else None,
                'irrigation_duration': fs.irrigation_duration if fs else None,
                'farm_notes':   fs.notes        if fs else '',
            })
        return Response(data)


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            return Response({'detail': 'Cannot delete your own account.'}, status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        is_active = request.data.get('is_active')
        if is_active is not None:
            user.is_active = bool(is_active)
            user.save(update_fields=['is_active'])
        return Response({'id': user.id, 'is_active': user.is_active})


class AdminDeviceListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        devices = Device.objects.select_related('user').order_by('-created_at')
        data = [
            {
                'id':           d.id,
                'device_id':    d.device_id,
                'pairing_code': d.pairing_code,
                'secret_key':   d.secret_key,
                'device_name':  d.device_name,
                'status':       d.status,
                'is_paired':    d.is_paired,
                'crop_type':    d.crop_type,
                'soil_type':    d.soil_type,
                'last_seen':    d.last_seen,
                'created_at':   d.created_at,
                'paired_at':    d.paired_at,
                'owner_id':     d.user.id,
                'owner_name':   d.user.full_name,
                'owner_email':  d.user.email or d.user.phone_number,
                'total_readings': SensorReading.objects.filter(device=d).count(),
            }
            for d in devices
        ]
        return Response(data)


class AdminDeviceDetailView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        device = get_object_or_404(Device, pk=pk)
        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminGenerateDeviceView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        def gen_device_id():
            return 'EF-' + uuid.uuid4().hex[:8].upper()

        def gen_pairing_code():
            chars = string.ascii_uppercase + string.digits
            return ''.join(secrets.choice(chars) for _ in range(6))

        def gen_secret_key():
            return secrets.token_hex(32)

        # Ensure uniqueness
        device_id = gen_device_id()
        while Device.objects.filter(device_id=device_id).exists():
            device_id = gen_device_id()

        pairing_code = gen_pairing_code()
        while Device.objects.filter(pairing_code=pairing_code).exists():
            pairing_code = gen_pairing_code()

        secret_key = gen_secret_key()

        # Save the device record so users can pair it later
        Device.objects.create(
            user=request.user,
            device_id=device_id,
            pairing_code=pairing_code,
            secret_key=secret_key,
            device_name=f'Device {device_id}',
            is_paired=False,
            status='Offline',
        )

        return Response({
            'device_id':    device_id,
            'pairing_code': pairing_code,
            'secret_key':   secret_key,
        }, status=status.HTTP_200_OK)


class AdminDeviceStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        from django.utils import timezone
        from datetime import timedelta

        device  = get_object_or_404(Device, pk=pk)
        latest  = SensorReading.objects.filter(device=device).first()
        total   = SensorReading.objects.filter(device=device).count()
        now     = timezone.now()

        reading = None
        if latest:
            reading = {
                'soil_moisture': latest.soil_moisture,
                'temperature':   latest.temperature,
                'humidity':      latest.humidity,
                'water_tank':    latest.water_tank,
                'pump_status':   latest.pump_status,
                'irrig_cycles':  latest.irrig_cycles,
                'recorded_at':   latest.recorded_at,
            }

        # ── Diagnostics engine ───────────────────────────────────────────────
        issues = []

        def issue(severity, title, reason, fix):
            issues.append({'severity': severity, 'title': title, 'reason': reason, 'fix': fix})

        # 1. Not paired at all
        if not device.is_paired:
            issue('critical', 'Device Not Paired',
                  'This device has never been paired to any user account.',
                  'Share the Device ID and Pairing Code with the user so they can pair it from the Connect Device page.')

        # 2. Paired but never sent data
        elif total == 0:
            issue('critical', 'No Data Received',
                  'Device is paired but has never sent any sensor readings to the server.',
                  'Check that the device firmware has the correct Device ID and Secret Key, and that it can reach the API endpoint /api/sensor/ingest/.')

        # 3. Offline — was online before
        if device.is_paired and device.status == 'Offline' and device.last_seen:
            minutes_ago = (now - device.last_seen).total_seconds() / 60
            hours_ago   = minutes_ago / 60
            if hours_ago > 24:
                issue('critical', 'Device Offline — Long Duration',
                      f'Device has been offline for {int(hours_ago)} hours (last seen {device.last_seen.strftime("%Y-%m-%d %H:%M")}).',
                      'Check power supply, Wi-Fi connection, and that the device is physically running. Verify the device can reach the internet.')
            elif hours_ago > 1:
                issue('high', 'Device Offline',
                      f'Device went offline {int(hours_ago)} hour(s) ago.',
                      'Device may have lost power or Wi-Fi. Check the physical device and router.')
            else:
                issue('medium', 'Device Recently Offline',
                      f'Device went offline {int(minutes_ago)} minute(s) ago.',
                      'This may be a temporary dropout. Wait a few minutes and refresh.')

        # 4. Paired but status still Offline and never seen
        if device.is_paired and device.status == 'Offline' and not device.last_seen and total == 0:
            issue('critical', 'Never Connected After Pairing',
                  'Device was paired but has never come online or sent data.',
                  'Ensure the device firmware is flashed correctly with the right credentials and the device has internet access.')

        # 5. Stale data — online but readings are old
        if device.status == 'Online' and latest:
            age_minutes = (now - latest.recorded_at).total_seconds() / 60
            if age_minutes > 30:
                issue('high', 'Stale Sensor Data',
                      f'Device shows Online but last reading was {int(age_minutes)} minutes ago.',
                      'The device may be stuck in a loop or the sensor reporting interval is too long. Check firmware.')

        # 6. Sensor value anomalies
        if latest:
            if latest.soil_moisture is None:
                issue('high', 'Soil Moisture Sensor Missing',
                      'Soil moisture value is null in the latest reading.',
                      'Check the soil moisture sensor wiring and calibration on the device.')
            elif latest.soil_moisture < 0 or latest.soil_moisture > 100:
                issue('medium', 'Soil Moisture Out of Range',
                      f'Soil moisture reading is {latest.soil_moisture}% which is outside 0–100%.',
                      'Sensor may be damaged or miscalibrated. Check wiring and recalibrate.')

            if latest.temperature is None:
                issue('high', 'Temperature Sensor Missing',
                      'Temperature value is null in the latest reading.',
                      'Check the temperature/humidity sensor (e.g. DHT22) wiring.')
            elif latest.temperature < -10 or latest.temperature > 60:
                issue('medium', 'Temperature Out of Range',
                      f'Temperature reading is {latest.temperature}°C which seems abnormal.',
                      'Sensor may be faulty or exposed to extreme conditions.')

            if latest.humidity is None:
                issue('medium', 'Humidity Sensor Missing',
                      'Humidity value is null in the latest reading.',
                      'Check the humidity sensor wiring and connections.')

            if latest.water_tank is not None and latest.water_tank < 10:
                issue('high', 'Water Tank Critically Low',
                      f'Water tank level is at {latest.water_tank}%.',
                      'Refill the water tank immediately to avoid irrigation failure.')

        # 7. No crop/soil configured
        if device.is_paired:
            if not device.crop_type:
                issue('low', 'No Crop Type Set',
                      'Crop type has not been configured for this device.',
                      'User should set the crop type in Farm Settings for accurate irrigation planning.')
            if not device.soil_type:
                issue('low', 'No Soil Type Set',
                      'Soil type has not been configured for this device.',
                      'User should set the soil type in Farm Settings.')

        # 8. User account inactive
        if not device.user.is_active:
            issue('high', 'Owner Account Disabled',
                  f'The device owner ({device.user.full_name}) account is currently deactivated.',
                  'Reactivate the user account from the Admin Users panel.')

        return Response({
            'id':             device.id,
            'device_id':      device.device_id,
            'device_name':    device.device_name,
            'pairing_code':   device.pairing_code,
            'secret_key':     device.secret_key,
            'status':         device.status,
            'is_paired':      device.is_paired,
            'crop_type':      device.crop_type,
            'soil_type':      device.soil_type,
            'last_seen':      device.last_seen,
            'created_at':     device.created_at,
            'paired_at':      device.paired_at,
            'owner_id':       device.user.id,
            'owner_name':     device.user.full_name,
            'owner_email':    device.user.email or device.user.phone_number,
            'owner_active':   device.user.is_active,
            'latest_reading': reading,
            'total_readings': total,
            'diagnostics':    issues,
        })


class AdminDeviceFixView(APIView):
    """Admin takes control: fix device config, force pair, reset, update crop/soil"""
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        from django.utils import timezone
        device = get_object_or_404(Device, pk=pk)
        action = request.data.get('action')
        log = []

        if action == 'force_pair':
            # Assign device to a specific user and mark as paired
            user_id = request.data.get('user_id')
            if user_id:
                target = get_object_or_404(User, pk=user_id)
                device.user      = target
                device.is_paired = True
                device.paired_at = timezone.now()
                device.save(update_fields=['user', 'is_paired', 'paired_at'])
                log.append(f'Device force-paired to {target.full_name}.')
            else:
                return Response({'detail': 'user_id required for force_pair.'}, status=status.HTTP_400_BAD_REQUEST)

        elif action == 'unpair':
            # Reset pairing so user can re-pair
            device.is_paired = False
            device.paired_at = None
            device.status    = 'Offline'
            device.save(update_fields=['is_paired', 'paired_at', 'status'])
            log.append('Device unpaired. User can now re-pair with the same credentials.')

        elif action == 'reset_credentials':
            # Generate new pairing code and secret key
            chars = __import__('string').ascii_uppercase + __import__('string').digits
            new_pairing = ''.join(__import__('secrets').choice(chars) for _ in range(6))
            while Device.objects.filter(pairing_code=new_pairing).exclude(pk=pk).exists():
                new_pairing = ''.join(__import__('secrets').choice(chars) for _ in range(6))
            new_secret = __import__('secrets').token_hex(32)
            device.pairing_code = new_pairing
            device.secret_key   = new_secret
            device.is_paired    = False
            device.paired_at    = None
            device.save(update_fields=['pairing_code', 'secret_key', 'is_paired', 'paired_at'])
            log.append(f'Credentials reset. New pairing code: {new_pairing}')

        elif action == 'update_config':
            # Update device name, crop type, soil type
            fields = []
            for field in ['device_name', 'crop_type', 'soil_type']:
                val = request.data.get(field)
                if val is not None:
                    setattr(device, field, val)
                    fields.append(field)
            if fields:
                device.save(update_fields=fields)
                log.append(f'Updated: {", ".join(fields)}.')

        elif action == 'force_online':
            device.status    = 'Online'
            device.last_seen = timezone.now()
            device.save(update_fields=['status', 'last_seen'])
            log.append('Device status forced to Online.')

        elif action == 'force_offline':
            device.status = 'Offline'
            device.save(update_fields=['status'])
            log.append('Device status forced to Offline.')

        elif action == 'update_farm_settings':
            # Admin updates the user's farm settings on their behalf
            fs, _ = FarmSettings.objects.get_or_create(user=device.user)
            fields = []
            for field in ['soil_type', 'plant_type', 'moisture_min', 'moisture_max',
                          'moisture_critical_low', 'irrigation_duration', 'notes']:
                val = request.data.get(field)
                if val is not None:
                    setattr(fs, field, val)
                    fields.append(field)
            if fields:
                fs.save(update_fields=fields)
                log.append(f'Farm settings updated for {device.user.full_name}: {", ".join(fields)}.')
        else:
            return Response({'detail': f'Unknown action: {action}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': True,
            'log':     log,
            'device_id':    device.device_id,
            'device_name':  device.device_name,
            'is_paired':    device.is_paired,
            'status':       device.status,
            'pairing_code': device.pairing_code,
            'crop_type':    device.crop_type,
            'soil_type':    device.soil_type,
        })


class AdminWeatherView(APIView):
    """Admin weather dashboard — status, usage logs, per-user access control"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        from django.conf import settings as django_settings
        from api.models import WeatherAccessLog
        from django.utils import timezone
        from datetime import timedelta

        api_key = getattr(django_settings, 'OPENWEATHER_API_KEY', '')
        api_active = bool(api_key)

        # Test the API key live
        api_working = False
        api_error   = ''
        if api_active:
            try:
                import urllib.request, json
                url = f'https://api.openweathermap.org/data/2.5/weather?lat=0&lon=0&appid={api_key}'
                with urllib.request.urlopen(url, timeout=5) as r:
                    d = json.loads(r.read().decode())
                    api_working = 'weather' in d or 'main' in d
            except Exception as e:
                api_error = str(e)

        # Usage stats
        now   = timezone.now()
        logs  = WeatherAccessLog.objects.all()
        today = logs.filter(accessed_at__date=now.date()).count()
        week  = logs.filter(accessed_at__gte=now - timedelta(days=7)).count()
        total = logs.count()

        # Recent 20 logs
        recent = [
            {
                'user_name':  l.user.full_name,
                'user_email': l.user.email or l.user.phone_number,
                'location':   l.location,
                'lat':        l.lat,
                'lon':        l.lon,
                'success':    l.success,
                'accessed_at': l.accessed_at,
            }
            for l in logs[:20]
        ]

        # Per-user access list
        users = User.objects.filter(is_staff=False).order_by('full_name')
        user_access = [
            {
                'id':             u.id,
                'full_name':      u.full_name,
                'email':          u.email or u.phone_number,
                'weather_access': getattr(u, 'weather_access', True),
                'usage_count':    WeatherAccessLog.objects.filter(user=u).count(),
                'last_used':      WeatherAccessLog.objects.filter(user=u).values_list('accessed_at', flat=True).first(),
            }
            for u in users
        ]

        return Response({
            'api_key_set':   api_active,
            'api_working':   api_working,
            'api_error':     api_error,
            'api_key_hint':  (api_key[:6] + '…' + api_key[-4:]) if len(api_key) > 10 else ('Not set' if not api_key else api_key),
            'stats': {
                'today': today,
                'week':  week,
                'total': total,
            },
            'recent_logs':  recent,
            'user_access':  user_access,
        })

    def patch(self, request):
        """Toggle weather access for a specific user"""
        user_id = request.data.get('user_id')
        access  = request.data.get('weather_access')
        if user_id is None or access is None:
            return Response({'detail': 'user_id and weather_access required.'}, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, pk=user_id)
        user.weather_access = bool(access)
        user.save(update_fields=['weather_access'])
        return Response({'id': user.id, 'weather_access': user.weather_access})
