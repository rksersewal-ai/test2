# =============================================================================
# FILE: apps/core/auth_views.py
# BUG FIX #7: MeView was missing permission_classes = [IsAuthenticated].
#   Without it, the view relies on DEFAULT_PERMISSION_CLASSES from settings.
#   If that is ever set to AllowAny (dev testing, misconfiguration) this
#   endpoint would crash with AttributeError on AnonymousUser.full_name.
#   Explicit declaration is required for a compliance system.
# =============================================================================
import logging

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

logger = logging.getLogger(__name__)


def _user_payload(user):
    return {
        'full_name': user.full_name or user.username,
        'username':  user.username,
        'email':     user.email,
        'is_staff':  user.is_staff,
        'role':      user.role,
        'section':   user.section.name if user.section else '',
    }


class CookieTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['full_name'] = user.full_name or user.username
        token['role']      = user.role
        token['section']   = user.section.name if user.section else ''
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update(_user_payload(self.user))
        return data


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CookieTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code != status.HTTP_200_OK:
            return response

        access_token  = response.data.get('access')
        refresh_token = response.data.get('refresh')
        jwt_settings  = settings.SIMPLE_JWT
        secure        = not settings.DEBUG

        body = {
            key: response.data[key]
            for key in ('access', 'refresh', 'full_name', 'username', 'email', 'is_staff', 'role', 'section')
        }
        result = Response(body, status=status.HTTP_200_OK)
        result.set_cookie(
            'access_token',
            access_token,
            max_age=int(jwt_settings['ACCESS_TOKEN_LIFETIME'].total_seconds()),
            httponly=True,
            secure=secure,
            samesite='Lax',
            path='/',
        )
        result.set_cookie(
            'refresh_token',
            refresh_token,
            max_age=int(jwt_settings['REFRESH_TOKEN_LIFETIME'].total_seconds()),
            httponly=True,
            secure=secure,
            samesite='Lax',
            path='/api/v1/auth/token/refresh/',
        )
        return result


class CookieTokenRefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Refresh token not found.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        serializer.is_valid(raise_exception=True)

        data         = serializer.validated_data
        jwt_settings = settings.SIMPLE_JWT
        secure       = not settings.DEBUG

        result = Response({'detail': 'Token refreshed.'}, status=status.HTTP_200_OK)
        result.set_cookie(
            'access_token',
            data['access'],
            max_age=int(jwt_settings['ACCESS_TOKEN_LIFETIME'].total_seconds()),
            httponly=True,
            secure=secure,
            samesite='Lax',
            path='/',
        )
        if 'refresh' in data:
            result.set_cookie(
                'refresh_token',
                data['refresh'],
                max_age=int(jwt_settings['REFRESH_TOKEN_LIFETIME'].total_seconds()),
                httponly=True,
                secure=secure,
                samesite='Lax',
                path='/api/v1/auth/token/refresh/',
            )
        return result


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = Response({'detail': 'Logged out.'}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token',  path='/')
        response.delete_cookie('refresh_token', path='/api/v1/auth/token/refresh/')
        return response


class MeView(APIView):
    # BUG FIX #7: explicit permission — never rely on global default for user data endpoint
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(_user_payload(request.user))
