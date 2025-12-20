from bible_way.models import User
from bible_way.storage import UserDB, GoogleSignupResponseDTO
from bible_way.presenters.google_auth_response import GoogleAuthResponse
from bible_way.jwt_authentication.jwt_tokens import UserAuthentication
from rest_framework.response import Response
from firebase_admin import auth
from rest_framework import status
import random
import string


class GoogleAuthenticationInteractor:
    def __init__(self, storage: UserDB, response: GoogleAuthResponse, authentication: UserAuthentication):
        self.storage = storage
        self.response = response
        self.authentication = authentication
    
    def google_authentication_interactor(self, token: str, age: int = None, preferred_language: str = None, country: str = None) -> Response:
        try:
            if not token:
                return self.response.google_token_verification_failed_response()
                
            decoded_token = auth.verify_id_token(token)
            
            google_id = decoded_token['uid']
            email = decoded_token['email']
            name = decoded_token.get('name', '')
            
        except Exception as e:
            print(f"Token verification failed: {e}")
            return self.response.google_token_verification_failed_response()
        
        existing_google_user = self.storage.get_user_by_google_id(google_id)
        if existing_google_user:
            tokens = self.authentication.create_tokens(user=existing_google_user)
            response_dto = GoogleSignupResponseDTO(
                access_token=tokens['access'],
                refresh_token=tokens['refresh']
            )
            return self.response.google_auth_success_response(response_dto=response_dto, message="Login successful")
        
        email_exists, existing_user = self.storage.check_user_exists_by_email(email)
        if email_exists:
            if existing_user.auth_provider == 'EMAIL':
                existing_user = self.storage.update_user_auth_provider(existing_user, 'BOTH')
                existing_user.google_id = google_id
                existing_user.is_email_verified = True  # Google already verified the email
                existing_user.save()
            elif existing_user.auth_provider == 'GOOGLE':
                existing_user.google_id = google_id
                existing_user.save()
            
            tokens = self.authentication.create_tokens(user=existing_user)
            response_dto = GoogleSignupResponseDTO(
                access_token=tokens['access'],
                refresh_token=tokens['refresh']
            )
            return self.response.google_auth_success_response(response_dto=response_dto, message="Login successful")
        
        if age is None or preferred_language is None or preferred_language == '':
            return self.response.account_not_found_response()
        
        if not name:
            name = email.split('@')[0]

        # Generate username from name (max 150 chars for Django's AbstractUser)
        username = name.replace(' ', '_').lower()[:150]
        
        # Ensure username is unique
        while self.storage.get_user_by_username(username):
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            username = f"{username}_{random_suffix}"[:150]
        
        user = self.storage.create_google_user(
            username=username,
            email=email,
            google_id=google_id,
            country=country or "",
            age=age,
            preferred_language=preferred_language
        )
        
        tokens = self.authentication.create_tokens(user=user)
        response_dto = GoogleSignupResponseDTO(
            access_token=tokens['access'],
            refresh_token=tokens['refresh']
        )
        return self.response.google_auth_success_response(response_dto=response_dto, message="Google signup successful", status_code=status.HTTP_201_CREATED)

