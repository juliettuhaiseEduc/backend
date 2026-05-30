from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, LoginSerializer
from .models import User


def _token_response(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id':                 user.id,
            'full_name':          user.full_name,
            'email':              user.email,
            'phone_number':       user.phone_number,
            'is_staff':           user.is_staff,
            'must_change_password': getattr(user, 'must_change_password', False),
            'weather_access':     getattr(user, 'weather_access', True),
            'admin_level':        getattr(user, 'admin_level', 'user'),
            'can_manage_users':   getattr(user, 'can_manage_users', False),
            'can_manage_devices': getattr(user, 'can_manage_devices', False),
            'can_manage_weather': getattr(user, 'can_manage_weather', False),
            'can_manage_system':  getattr(user, 'can_manage_system', False),
        },
    }


class CheckIdentifierView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        value = request.query_params.get('value', '').strip()
        if not value:
            return Response({'available': False})
        taken = (
            User.objects.filter(email=value).exists() or
            User.objects.filter(phone_number=value).exists()
        )
        return Response({'available': not taken})


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            from api.models import FarmSettings
            FarmSettings.objects.get_or_create(user=user)
            return Response(_token_response(user), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            from django.utils import timezone
            user = serializer.validated_data['user']
            user.last_seen = timezone.now()
            user.save(update_fields=['last_seen'])
            return Response(_token_response(user))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """Returns the authenticated user's profile from the database — never from client input."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id':                   user.id,
            'full_name':            user.full_name,
            'email':                user.email,
            'phone_number':         user.phone_number,
            'farm_name':            user.farm_name,
            'is_staff':             user.is_staff,
            'must_change_password': user.must_change_password,
            'weather_access':       user.weather_access,
            'admin_level':          user.admin_level,
            'can_manage_users':     user.can_manage_users,
            'can_manage_devices':   user.can_manage_devices,
            'can_manage_weather':   user.can_manage_weather,
            'can_manage_system':    user.can_manage_system,
        })

    def patch(self, request):
        user = request.user
        data = request.data
        fields = []

        if 'full_name' in data:
            name = data['full_name'].strip()
            if not name:
                return Response({'detail': 'Name cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)
            user.full_name = name
            fields.append('full_name')

        if 'farm_name' in data:
            user.farm_name = data['farm_name'].strip()
            fields.append('farm_name')

        if 'email' in data:
            email = data['email'].strip()
            if email and User.objects.filter(email=email).exclude(pk=user.pk).exists():
                return Response({'detail': 'Email already in use.'}, status=status.HTTP_400_BAD_REQUEST)
            user.email = email or None
            fields.append('email')

        if 'phone_number' in data:
            phone = data['phone_number'].strip()
            if phone and User.objects.filter(phone_number=phone).exclude(pk=user.pk).exists():
                return Response({'detail': 'Phone number already in use.'}, status=status.HTTP_400_BAD_REQUEST)
            user.phone_number = phone or None
            fields.append('phone_number')

        if 'new_password' in data:
            current = data.get('current_password', '')
            if not user.check_password(current):
                return Response({'detail': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
            new_pass = data['new_password']
            if len(new_pass) < 8:
                return Response({'detail': 'Password must be at least 8 characters.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_pass)
            fields.append('password')

        if not fields:
            return Response({'detail': 'No changes provided.'}, status=status.HTTP_400_BAD_REQUEST)

        user.save(update_fields=fields)

        # Return fresh tokens if password changed so the session stays alive
        if 'password' in fields:
            return Response(_token_response(user))
        return Response({'detail': 'Profile updated.'})

    def delete(self, request):
        user = request.user
        current = request.data.get('current_password', '')
        if not user.check_password(current):
            return Response({'detail': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HeartbeatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.utils import timezone
        request.user.last_seen = timezone.now()
        request.user.save(update_fields=['last_seen'])
        return Response({'ok': True})


class SetPasswordView(APIView):
    """Called right after first login — sets permanent password, clears OTP flag."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        new_pass = request.data.get('new_password', '')
        if len(new_pass) < 8:
            return Response({'detail': 'Password must be at least 8 characters.'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        user.set_password(new_pass)
        user.must_change_password = False
        user.otp_code = ''
        user.save(update_fields=['password', 'must_change_password', 'otp_code'])
        return Response(_token_response(user))
