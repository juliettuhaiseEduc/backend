from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User
from api.models import Device


class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by('-id')
        data = [
            {
                'id':           u.id,
                'full_name':    u.full_name,
                'email':        u.email,
                'phone_number': u.phone_number,
                'is_staff':     u.is_staff,
                'is_active':    u.is_active,
                'created_at':   u.created_at,
                'device_count': u.devices.count(),
            }
            for u in users
        ]
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
                'id':          d.id,
                'device_id':   d.device_id,
                'device_name': d.device_name,
                'status':      d.status,
                'is_paired':   d.is_paired,
                'crop_type':   d.crop_type,
                'last_seen':   d.last_seen,
                'created_at':  d.created_at,
                'owner_id':    d.user.id,
                'owner_name':  d.user.full_name,
                'owner_email': d.user.email or d.user.phone_number,
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
