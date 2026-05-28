from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, LoginSerializer
from .models import User


def _token_response(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id':           user.id,
            'full_name':    user.full_name,
            'email':        user.email,
            'phone_number': user.phone_number,
            'is_staff':     user.is_staff,
            'weather_access': getattr(user, 'weather_access', True),
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
            return Response(_token_response(serializer.validated_data['user']))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
