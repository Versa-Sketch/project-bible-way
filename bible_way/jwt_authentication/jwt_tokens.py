from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from bible_way.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['email'] = self.user.email
        data['user_id'] = str(self.user.user_id)
        data['user_name'] = self.user.username  # Map username to user_name for API response
        return data


class UserAuthentication:
    def create_tokens(self, user: User):
        refresh = RefreshToken.for_user(user)
        
        refresh['email'] = user.email
        refresh['user_id'] = str(user.user_id)
        refresh['user_name'] = user.username  # Map username to user_name for API response
        refresh['is_staff'] = user.is_staff
        refresh['is_superuser'] = user.is_superuser
        
        access_token = refresh.access_token
        access_token['email'] = user.email
        access_token['user_id'] = str(user.user_id)
        access_token['user_name'] = user.username  # Map username to user_name for API response
        access_token['is_staff'] = user.is_staff
        access_token['is_superuser'] = user.is_superuser
        
        return {
            'access': str(access_token),
            'refresh': str(refresh)
        }
