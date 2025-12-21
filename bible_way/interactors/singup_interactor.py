from bible_way.models import User
from bible_way.storage import UserDB, SignupResponseDTO
from bible_way.presenters.singup_response import SignupResponse
from bible_way.jwt_authentication.jwt_tokens import UserAuthentication
from rest_framework.response import Response
from django.db import IntegrityError
from bible_way.utils.otp_generator import generate_otp, get_otp_expiry
from bible_way.utils.email_service import ZeptoMailService
import logging
import re

logger = logging.getLogger(__name__)


class SignupInteractor:
    def __init__(self, storage: UserDB, response: SignupResponse, authentication: UserAuthentication):
        self.storage = storage
        self.response = response
        self.authentication = authentication
    
    def signup_interactor(self, user_name: str, email: str, password: str, 
                          country: str, age: int, preferred_language: str, 
                          confirm_password: str) -> Response:
        
        # Validate required fields
        if not user_name or (isinstance(user_name, str) and not user_name.strip()):
            return self.response.validation_error_response("Username is required")
        
        if not email or (isinstance(email, str) and not email.strip()):
            return self.response.validation_error_response("Email is required")
        
        if not password or (isinstance(password, str) and not password.strip()):
            return self.response.validation_error_response("Password is required")
        
        if not confirm_password or (isinstance(confirm_password, str) and not confirm_password.strip()):
            return self.response.validation_error_response("Confirm password is required")
        
        if not country or (isinstance(country, str) and not country.strip()):
            return self.response.validation_error_response("Country is required")
        
        # Trim whitespace
        user_name = user_name.strip()
        email = email.strip().lower()
        password = password.strip()
        confirm_password = confirm_password.strip()
        country = country.strip()
        
        # Validate username format and length
        if len(user_name) < 3:
            return self.response.validation_error_response("Username must be at least 3 characters long")
        
        if len(user_name) > 150:
            return self.response.validation_error_response("Username must be 150 characters or fewer")
        
        
        # Validate password strength
        if len(password) < 8:
            return self.response.validation_error_response("Password must be at least 8 characters long")
        
        # Validate passwords match
        if password != confirm_password:
            return self.response.password_does_not_match()
        
        # Validate age if provided
        if age is not None:
            try:
                age_int = int(age)
                if age_int < 1 or age_int > 150:
                    return self.response.validation_error_response("Age must be between 1 and 150")
            except (ValueError, TypeError):
                return self.response.validation_error_response("Age must be a valid number")
        
        # Validate preferred_language if provided (should not contain numbers)
        if preferred_language:
            preferred_language = preferred_language.strip()
            # Check if preferred_language contains any digits
            if re.search(r'\d', preferred_language):
                return self.response.validation_error_response("Preferred language cannot contain numbers")

        email_exists, existing_user = self.storage.check_user_exists_by_email(email)
        if email_exists:
            if existing_user.auth_provider == 'GOOGLE':
                existing_user = self.storage.update_user_auth_provider(existing_user, 'BOTH')
                from django.contrib.auth.hashers import make_password
                existing_user.password = make_password(password)
                existing_user.is_email_verified = True  # Google already verified the email
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
        
        # Map API user_name to username (Django's AbstractUser field)
        username = user_name
        
        # Check if username already exists
        if self.storage.get_user_by_username(username):
            return self.response.user_username_exists_response()
        
        try:
            user = self.storage.create_user(
                username=username,      # Use username from AbstractUser
                email=email,
                password=password,
                country=country,
                age=age,
                preferred_language=preferred_language
            )
        except IntegrityError as e:
            # Handle race condition or any other integrity constraint violations
            if 'username' in str(e):
                return self.response.user_username_exists_response()
            elif 'email' in str(e):
                return self.response.user_email_exists_response()
            else:
                return self.response.internal_server_error_response()
    
        # Generate OTP and send verification email
        otp = generate_otp()
        otp_expiry = get_otp_expiry()
        
        # Update user with OTP
        user = self.storage.update_user_otp(user, otp, otp_expiry)
        
        # Send verification email
        email_service = ZeptoMailService()
        email_sent, email_message = email_service.send_verification_email(
            user_email=email,
            user_name=username,
            otp=otp
        )
        
        if not email_sent:
            logger.error(f"Failed to send verification email to {email}: {email_message}")
            # Still return success but log the error
            # User can request resend later
        
        # Return email verification required response (no tokens)
        return self.response.email_verification_required_response()