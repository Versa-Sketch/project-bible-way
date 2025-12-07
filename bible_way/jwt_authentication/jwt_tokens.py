from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from bible_way.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Add custom claims
        data['email'] = self.user.email
        data['user_id'] = str(self.user.user_id)
        data['user_name'] = self.user.user_name
        return data


class UserAuthentication:
    def create_tokens(self, user: User):
        # Use the standard RefreshToken.for_user() method
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims to both refresh and access tokens
        refresh['email'] = user.email
        refresh['user_id'] = str(user.user_id)
        refresh['user_name'] = user.user_name
        
        # The access token will inherit the claims from the refresh token
        access_token = refresh.access_token
        access_token['email'] = user.email
        access_token['user_id'] = str(user.user_id)
        access_token['user_name'] = user.user_name
        
        return {
            'access': str(access_token),
            'refresh': str(refresh)
        }
