# =============================================================================
# FILE: backend/edms/auth.py
# Custom JWT token serializer — injects full_name, role, section into
# the login response so the frontend can display user info immediately.
#
# Also provides:
#   - CustomTokenObtainPairView  — replaces default TokenObtainPairView
#   - httpOnly cookie setter      — sets access + refresh as secure cookies
# =============================================================================
from django.conf import settings
from django.http import JsonResponse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status


class EDMSTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the default JWT payload with user profile fields.
    These are embedded in the token AND returned in the JSON body
    so the React frontend can read them without a separate /me/ call.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # ── Claims embedded in JWT payload (decoded by frontend if needed) ──
        token['full_name'] = user.get_full_name() or user.username
        token['username']  = user.username
        token['email']     = user.email
        token['is_staff']  = user.is_staff
        # Profile fields — graceful fallback if profile model not yet created
        profile = getattr(user, 'profile', None)
        token['role']      = getattr(profile, 'role',    'user')
        token['section']   = getattr(profile, 'section', '')
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        profile = getattr(user, 'profile', None)
        # ── Extra fields in JSON response body ──
        data['full_name'] = user.get_full_name() or user.username
        data['username']  = user.username
        data['email']     = user.email
        data['is_staff']  = user.is_staff
        data['role']      = getattr(profile, 'role',    'user')
        data['section']   = getattr(profile, 'section', '')
        return data


class EDMSTokenObtainPairView(TokenObtainPairView):
    """
    POST /api/v1/auth/token/
    Sets access + refresh tokens as httpOnly cookies AND returns
    user profile in JSON body for React state initialisation.
    """
    serializer_class = EDMSTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code != 200:
            return response

        data           = response.data
        access_token   = data.get('access')
        refresh_token  = data.get('refresh')

        jwt_settings   = settings.SIMPLE_JWT
        access_max_age = int(jwt_settings['ACCESS_TOKEN_LIFETIME'].total_seconds())
        refresh_max_age= int(jwt_settings['REFRESH_TOKEN_LIFETIME'].total_seconds())
        secure         = not settings.DEBUG   # True in production HTTPS
        samesite       = 'Lax'

        # Build clean response body — no raw tokens exposed to JS
        body = {
            'full_name': data.get('full_name'),
            'username':  data.get('username'),
            'email':     data.get('email'),
            'is_staff':  data.get('is_staff'),
            'role':      data.get('role'),
            'section':   data.get('section'),
        }

        res = Response(body, status=status.HTTP_200_OK)

        # Set httpOnly cookies — invisible to JavaScript
        res.set_cookie(
            'access_token',
            access_token,
            max_age=access_max_age,
            httponly=True,
            secure=secure,
            samesite=samesite,
            path='/',
        )
        res.set_cookie(
            'refresh_token',
            refresh_token,
            max_age=refresh_max_age,
            httponly=True,
            secure=secure,
            samesite=samesite,
            path='/api/v1/auth/token/refresh/',  # restrict refresh cookie path
        )
        return res


class EDMSTokenRefreshView(__import__('rest_framework_simplejwt.views', fromlist=['TokenRefreshView']).TokenRefreshView):
    """
    POST /api/v1/auth/token/refresh/
    Reads refresh token from httpOnly cookie, rotates it,
    sets new access + refresh cookies.
    """
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Refresh token not found.'}, status=401)

        # Inject cookie value into request data
        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            jwt_settings    = settings.SIMPLE_JWT
            access_max_age  = int(jwt_settings['ACCESS_TOKEN_LIFETIME'].total_seconds())
            refresh_max_age = int(jwt_settings['REFRESH_TOKEN_LIFETIME'].total_seconds())
            secure          = not settings.DEBUG

            res = Response({'detail': 'Token refreshed.'}, status=200)
            res.set_cookie('access_token',  response.data['access'],
                           max_age=access_max_age,  httponly=True,
                           secure=secure, samesite='Lax', path='/')
            if 'refresh' in response.data:
                res.set_cookie('refresh_token', response.data['refresh'],
                               max_age=refresh_max_age, httponly=True,
                               secure=secure, samesite='Lax',
                               path='/api/v1/auth/token/refresh/')
            return res
        return response


class EDMSLogoutView(__import__('rest_framework.views', fromlist=['APIView']).APIView):
    """
    POST /api/v1/auth/logout/
    Clears httpOnly cookies server-side.
    """
    permission_classes = []

    def post(self, request, *args, **kwargs):
        res = Response({'detail': 'Logged out.'}, status=200)
        res.delete_cookie('access_token',  path='/')
        res.delete_cookie('refresh_token', path='/api/v1/auth/token/refresh/')
        return res
