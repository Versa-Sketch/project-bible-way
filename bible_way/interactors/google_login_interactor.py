from bible_way.models import User
from bible_way.storage import UserDB, GoogleLoginResponseDTO
from bible_way.presenters.google_auth_response import GoogleAuthResponse
from bible_way.jwt_authentication.jwt_tokens import UserAuthentication
from rest_framework.response import Response


class GoogleLoginInteractor:
    def __init__(self, storage: UserDB, response: GoogleAuthResponse, authentication: UserAuthentication):
        self.storage = storage
        self.response = response
        self.authentication = authentication
    
    def google_login_interactor(self, google_id: str, email: str) -> Response:
        user = self.storage.get_user_by_google_id(google_id)
        if user:
            tokens = self.authentication.create_tokens(user=user)
            response_dto = GoogleLoginResponseDTO(
                access_token=tokens['access'],
                refresh_token=tokens['refresh']
            )
            return self.response.google_auth_success_response(response_dto=response_dto, message="Login successful")
        
        email_exists, user = self.storage.check_user_exists_by_email(email)
        if email_exists:
            if user.auth_provider == 'EMAIL':
                user = self.storage.update_user_auth_provider(user, 'BOTH')
                user.google_id = google_id
                user.save()
            elif user.auth_provider == 'GOOGLE':
                user.google_id = google_id
                user.save()
            
            tokens = self.authentication.create_tokens(user=user)
            response_dto = GoogleLoginResponseDTO(
                access_token=tokens['access'],
                refresh_token=tokens['refresh']
            )
            return self.response.google_auth_success_response(response_dto=response_dto, message="Login successful")
        
        return self.response.google_user_not_found_response()

