from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from bible_way.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Add custom claims
        data['role'] = self.user.role
        data['email'] = self.user.email
        data['user_id'] = str(self.user.user_id)
        return data


class UserAuthentication:
    def create_tokens(self, user: User):
        # Use the standard RefreshToken.for_user() method
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims to both refresh and access tokens
        refresh['role'] = user.role
        refresh['email'] = user.email
        refresh['user_id'] = str(user.user_id)
        
        # The access token will inherit the claims from the refresh token
        access_token = refresh.access_token
        access_token['role'] = user.role
        access_token['email'] = user.email
        access_token['user_id'] = str(user.user_id)
        
        return {
            'access': str(access_token),
            'refresh': str(refresh)
        }
