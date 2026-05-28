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
