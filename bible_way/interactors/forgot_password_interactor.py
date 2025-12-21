from bible_way.storage import UserDB
from bible_way.presenters.forgot_password_response import ForgotPasswordResponse
from bible_way.utils.otp_generator import generate_otp, get_otp_expiry
from bible_way.utils.email_service import ZeptoMailService
from bible_way.models import AuthProviderChoices
from rest_framework.response import Response
import re
import logging

logger = logging.getLogger(__name__)


class ForgotPasswordInteractor:
    def __init__(self, storage: UserDB, response: ForgotPasswordResponse):
        self.storage = storage
        self.response = response
    
    def forgot_password_interactor(self, email: str) -> Response:
        """
        Send password reset OTP to user's email
        
        Args:
            email: User's email address
            
        Returns:
            Response indicating success or failure
        """
        # Validate email format
        if not email or (isinstance(email, str) and not email.strip()):
            return self.response.validation_error_response("Email is required")
        
        email = email.strip().lower()
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return self.response.validation_error_response("Invalid email format")
        
        # Get user by email
        user = self.storage.get_user_by_email(email)
        if not user:
            # Return success to prevent email enumeration attacks
            # But log for debugging
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return self.response.otp_sent_success_response()
        
        # Check if user uses email authentication (not GOOGLE only)
        if user.auth_provider == AuthProviderChoices.GOOGLE:
            return self.response.invalid_auth_provider_response()
        
        # Generate OTP and expiry
        otp = generate_otp()
        otp_expiry = get_otp_expiry()
        
        # Update user with password reset OTP
        user = self.storage.update_password_reset_otp(user, otp, otp_expiry)
        
        # Send password reset email
        email_service = ZeptoMailService()
        email_sent, email_message = email_service.send_password_reset_email(
            user_email=email,
            user_name=user.username,
            otp=otp
        )
        
        if not email_sent:
            logger.error(f"Failed to send password reset email to {email}: {email_message}")
            # Still return success to prevent email enumeration
            # Log the error for debugging
        
        return self.response.otp_sent_success_response()

