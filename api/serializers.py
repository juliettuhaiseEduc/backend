from rest_framework import serializers
from .models import Device, Notification, FarmSettings


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Device
        fields = ['id', 'device_id', 'device_name', 'crop_type', 'soil_type', 'status', 'last_seen', 'is_paired', 'paired_at']
        read_only_fields = ['id', 'device_id', 'last_seen', 'paired_at']


class ConnectDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Device
        fields = ['device_id', 'secret_key', 'device_name', 'crop_type', 'soil_type']

    def validate_device_id(self, value):
        if Device.objects.filter(device_id=value).exists():
            raise serializers.ValidationError('A device with this ID is already registered.')
        return value

    def create(self, validated_data):
        return Device.objects.create(user=self.context['request'].user, **validated_data)


class PairDeviceSerializer(serializers.Serializer):
    """Validate and pair a hardware device using Device ID and Pairing Code"""
    device_id    = serializers.CharField(max_length=100)
    pairing_code = serializers.CharField(max_length=20)

    def validate(self, attrs):
        device_id    = attrs.get('device_id')
        pairing_code = attrs.get('pairing_code')

        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            raise serializers.ValidationError({'device_id': 'Device not found. Check your Device ID.'})

        if device.pairing_code != pairing_code:
            raise serializers.ValidationError({'pairing_code': 'Invalid pairing code.'})

        if device.is_paired:
            raise serializers.ValidationError({'device_id': 'Device is already paired to an account.'})

        attrs['device'] = device
        return attrs

    def save(self):
        device = self.validated_data['device']
        user   = self.context['request'].user
        from django.utils import timezone
        device.user      = user
        device.is_paired = True
        device.paired_at = timezone.now()
        device.status    = 'Online'
        device.save()
        return device


class TestDeviceSerializer(serializers.Serializer):
    """Test hardware device connection using Device ID and Test Code"""
    device_id = serializers.CharField(max_length=100)
    test_code = serializers.CharField(max_length=50)

    def validate(self, attrs):
        device_id = attrs.get('device_id')
        test_code = attrs.get('test_code')

        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            raise serializers.ValidationError({'device_id': 'Device not found. Check your Device ID.'})

        if not device.activation_token or device.activation_token != test_code:
            raise serializers.ValidationError({'test_code': 'Invalid test code.'})

        attrs['device'] = device
        return attrs


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ['id', 'type', 'title', 'message', 'device_name', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class FarmSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FarmSettings
        fields = [
            'soil_type', 'plant_type',
            'moisture_min', 'moisture_max', 'moisture_critical_low',
            'irrigation_duration', 'notes', 'updated_at',
        ]
        read_only_fields = ['updated_at']
