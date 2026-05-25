from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, LoginSerializer


def _token_response(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id':           user.id,
            'email':        user.email,
            'full_name':    user.full_name,
            'phone_number': user.phone_number,
            'farm_name':    user.farm_name,
            'country':      user.country,
        },
    }


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Bootstrap isolated data for this tenant on registration
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
