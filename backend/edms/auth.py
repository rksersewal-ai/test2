# =============================================================================
# FILE: backend/edms/auth.py
# BUG FIX: token/verify/ endpoint needs a valid access token in the request
# body when using header-based verification. With cookie auth, the frontend
# calls verify/ without a body — this causes simplejwt to return 400 not 401.
# Added a dedicated /api/v1/auth/me/ endpoint that just checks the cookie and
# returns 200 + user info (or 401) — used by AuthContext on mount.
# =============================================================================
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions


class EDMSTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['full_name'] = user.get_full_name() or user.username
        token['username']  = user.username
        token['email']     = user.email
        token['is_staff']  = user.is_staff
        profile = getattr(user, 'profile', None)
        token['role']      = getattr(profile, 'role',    'user')
        token['section']   = getattr(profile, 'section', '')
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        profile = getattr(user, 'profile', None)
        data['full_name'] = user.get_full_name() or user.username
        data['username']  = user.username
        data['email']     = user.email
        data['is_staff']  = user.is_staff
        data['role']      = getattr(profile, 'role',    'user')
        data['section']   = getattr(profile, 'section', '')
        return data


class EDMSTokenObtainPairView(TokenObtainPairView):
    """POST /api/v1/auth/token/  — sets access + refresh as httpOnly cookies."""
    serializer_class = EDMSTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code != 200:
            return response

        data            = response.data
        access_token    = data.get('access')
        refresh_token   = data.get('refresh')
        jwt_s           = settings.SIMPLE_JWT
        access_max_age  = int(jwt_s['ACCESS_TOKEN_LIFETIME'].total_seconds())
        refresh_max_age = int(jwt_s['REFRESH_TOKEN_LIFETIME'].total_seconds())
        secure          = not settings.DEBUG

        body = {
            'full_name': data.get('full_name'),
            'username':  data.get('username'),
            'email':     data.get('email'),
            'is_staff':  data.get('is_staff'),
            'role':      data.get('role'),
            'section':   data.get('section'),
        }
        res = Response(body, status=status.HTTP_200_OK)
        res.set_cookie('access_token',  access_token,  max_age=access_max_age,
                       httponly=True, secure=secure, samesite='Lax', path='/')
        res.set_cookie('refresh_token', refresh_token, max_age=refresh_max_age,
                       httponly=True, secure=secure, samesite='Lax',
                       path='/api/v1/auth/token/refresh/')
        return res


class EDMSTokenRefreshView(
    __import__('rest_framework_simplejwt.views', fromlist=['TokenRefreshView']).TokenRefreshView
):
    """POST /api/v1/auth/token/refresh/  — reads cookie, rotates, re-sets cookies."""
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Refresh token not found.'}, status=401)
        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            jwt_s           = settings.SIMPLE_JWT
            access_max_age  = int(jwt_s['ACCESS_TOKEN_LIFETIME'].total_seconds())
            refresh_max_age = int(jwt_s['REFRESH_TOKEN_LIFETIME'].total_seconds())
            secure          = not settings.DEBUG
            res = Response({'detail': 'Token refreshed.'}, status=200)
            res.set_cookie('access_token', response.data['access'],
                           max_age=access_max_age, httponly=True,
                           secure=secure, samesite='Lax', path='/')
            if 'refresh' in response.data:
                res.set_cookie('refresh_token', response.data['refresh'],
                               max_age=refresh_max_age, httponly=True,
                               secure=secure, samesite='Lax',
                               path='/api/v1/auth/token/refresh/')
            return res
        return response


class EDMSLogoutView(APIView):
    """POST /api/v1/auth/logout/  — deletes httpOnly cookies server-side."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        res = Response({'detail': 'Logged out.'}, status=200)
        res.delete_cookie('access_token',  path='/')
        res.delete_cookie('refresh_token', path='/api/v1/auth/token/refresh/')
        return res


class EDMSMeView(APIView):
    """
    GET /api/v1/auth/me/
    BUG FIX: Lightweight endpoint used by AuthContext on mount to verify
    the cookie is still valid. Returns 200 + user info or 401.
    Using JWTCookieAuthentication (set in settings DEFAULT_AUTHENTICATION_CLASSES).
    """
    def get(self, request, *args, **kwargs):
        user = request.user
        profile = getattr(user, 'profile', None)
        return Response({
            'full_name': user.get_full_name() or user.username,
            'username':  user.username,
            'email':     user.email,
            'is_staff':  user.is_staff,
            'role':      getattr(profile, 'role',    'user'),
            'section':   getattr(profile, 'section', ''),
        })
