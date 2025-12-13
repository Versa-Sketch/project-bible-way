from bible_way.models import User
from bible_way.storage import UserDB, GoogleSignupResponseDTO
from bible_way.presenters.google_auth_response import GoogleAuthResponse
from bible_way.jwt_authentication.jwt_tokens import UserAuthentication
from rest_framework.response import Response
from firebase_admin import auth

class GoogleAuthInteractor:
    def __init__(self, storage: UserDB, response: GoogleAuthResponse, authentication: UserAuthentication):
        self.storage = storage
        self.response = response
        self.authentication = authentication
    
    def google_signup_interactor(self, token: str, country: str, age: int, preferred_language: str) -> Response:
        try:
            if not token:
                return self.response.google_token_verification_failed_response()
                
            decoded_token = auth.verify_id_token(token)
            
            google_id = decoded_token['uid']
            email = decoded_token['email']
            name = decoded_token.get('name', '')
            profile_picture_url = decoded_token.get('picture', None)
            
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
                if profile_picture_url:
                    existing_user.profile_picture_url = profile_picture_url
                existing_user.save()
            tokens = self.authentication.create_tokens(user=existing_user)
            response_dto = GoogleSignupResponseDTO(
                access_token=tokens['access'],
                refresh_token=tokens['refresh']
            )
            return self.response.google_auth_success_response(response_dto=response_dto, message="Login successful")

        if not name:
            name = email.split('@')[0]

        username = name.replace(' ', '_').lower()[:150]
        user_name = name.replace(' ', '_').lower()[:255]
        
        base_user_name = user_name
        counter = 1
        while self.storage.get_user_by_user_name(user_name):
            user_name = f"{base_user_name}_{counter}"
            counter += 1
        
        user = self.storage.create_google_user(
            username=username,
            user_name=user_name,
            email=email,
            google_id=google_id,
            country=country or "",
            age=age or 0,
            preferred_language=preferred_language or "",
            profile_picture_url=profile_picture_url
        )
        
        tokens = self.authentication.create_tokens(user=user)
        response_dto = GoogleSignupResponseDTO(
            access_token=tokens['access'],
            refresh_token=tokens['refresh']
        )
        return self.response.google_auth_success_response(response_dto=response_dto, message="Google signup successful")
