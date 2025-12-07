from bible_way.models import User
from bible_way.storage import UserDB, LoginResponseDTO
from bible_way.presenters.login_response import LoginResponse
from bible_way.jwt_authentication.jwt_tokens import UserAuthentication
from rest_framework.response import Response


class LoginInteractor:
    def __init__(self, storage: UserDB, response: LoginResponse, authentication: UserAuthentication):
        self.storage = storage
        self.response = response
        self.authentication = authentication
    
    def login_interactor(self, email: str, password: str) -> Response:
        email_exists, existing_user = self.storage.check_user_exists_by_email(email)
        if email_exists:
            if existing_user.auth_provider == 'GOOGLE':
                return self.response.google_account_login_response()
        
        user = self.storage.authenticate_user(email=email, password=password)
        if not user:
            return self.response.invalid_credentials_response()
        
        tokens = self.authentication.create_tokens(user=user)
        
        response_dto = LoginResponseDTO(
            access_token=tokens['access'],
            refresh_token=tokens['refresh']
        )
        response = self.response.login_success_response(response_dto=response_dto)
        return response

