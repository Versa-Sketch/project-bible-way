from bible_way.storage import UserDB, LoginResponseDTO
from bible_way.presenters.verify_email_response import VerifyEmailResponse
from bible_way.jwt_authentication.jwt_tokens import UserAuthentication
from rest_framework.response import Response
from django.utils import timezone


class VerifyEmailInteractor:
    def __init__(self, storage: UserDB, response: VerifyEmailResponse, authentication: UserAuthentication):
        self.storage = storage
        self.response = response
        self.authentication = authentication
    
    def verify_email_interactor(self, email: str, otp: str) -> Response:
        """
        Verify user email with OTP code
        
        Args:
            email: User's email address
            otp: 4-digit OTP code
            
        Returns:
            Response with tokens if verification successful
        """
        # Get user by email
        user = self.storage.get_user_by_email(email)
        if not user:
            return self.response.user_not_found_response()
        
        # Check if email is already verified
        if user.is_email_verified:
            return self.response.email_already_verified_response()
        
        # Check if OTP exists
        if not user.email_verification_otp:
            return self.response.invalid_otp_response()
        
        # Check if OTP is expired
        if user.otp_expiry and user.otp_expiry < timezone.now():
            return self.response.expired_otp_response()
        
        # Verify OTP matches
        if user.email_verification_otp != otp:
            return self.response.invalid_otp_response()
        
        # Verify email and clear OTP
        user = self.storage.verify_user_email(user)
        
        # Generate tokens for immediate login
        tokens = self.authentication.create_tokens(user=user)
        
        response_dto = LoginResponseDTO(
            access_token=tokens['access'],
            refresh_token=tokens['refresh']
        )
        
        return self.response.verification_success_response(response_dto=response_dto)

