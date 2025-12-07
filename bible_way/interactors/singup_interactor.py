from bible_way.models import User
from bible_way.storage import UserDB, SignupResponseDTO
from bible_way.presenters.singup_response import SignupResponse
from bible_way.jwt_authentication.jwt_tokens import UserAuthentication
from rest_framework.response import Response


class SignupInteractor:
    def __init__(self, storage: UserDB, response: SignupResponse, authentication: UserAuthentication):
        self.storage = storage
        self.response = response
        self.authentication = authentication
    
    def signup_interactor(self, user_name: str, email: str, password: str, 
                          country: str, age: int, preferred_language: str, 
                          confirm_password: str, profile_picture_url: str = None) -> Response:
      
        if password != confirm_password:
            return self.response.password_does_not_match()
            

        email_exists, existing_user = self.storage.check_user_exists_by_email(email)
        if email_exists:
            if existing_user.auth_provider == 'GOOGLE':
                existing_user = self.storage.update_user_auth_provider(existing_user, 'BOTH')
                from django.contrib.auth.hashers import make_password
                existing_user.password = make_password(password)
                if profile_picture_url:
                    existing_user.profile_picture_url = profile_picture_url
                existing_user.save()
                tokens = self.authentication.create_tokens(user=existing_user)
                response_dto = SignupResponseDTO(
                    access_token=tokens['access'],
                    refresh_token=tokens['refresh']
                )
                return self.response.user_signup_success_response(response_dto=response_dto)
            elif existing_user.auth_provider == 'BOTH':
                return self.response.account_already_linked_response()
            else:
                return self.response.user_email_exists_response()
        
        if self.storage.get_user_by_user_name(user_name):
            return self.response.user_username_exists_response()
        
        username = user_name
        
        user = self.storage.create_user(
            username=username,      # Required by Django's AbstractUser
            user_name=user_name,    # Our custom field
            email=email,
            password=password,
            country=country,
            age=age,
            preferred_language=preferred_language,
            profile_picture_url=profile_picture_url
        )
    
        tokens = self.authentication.create_tokens(user=user)
        
        response_dto = SignupResponseDTO(
            access_token=tokens['access'],
            refresh_token=tokens['refresh']
        )
        response = self.response.user_signup_success_response(response_dto=response_dto)
        return response