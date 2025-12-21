from bible_way.storage import UserDB
from bible_way.presenters.reset_password_response import ResetPasswordResponse
from bible_way.models import AuthProviderChoices
from rest_framework.response import Response
from django.utils import timezone
import re
import logging

logger = logging.getLogger(__name__)


class ResetPasswordInteractor:
    def __init__(self, storage: UserDB, response: ResetPasswordResponse):
        self.storage = storage
        self.response = response
    
    def reset_password_interactor(
        self,
        email: str,
        otp: str,
        new_password: str,
        confirm_password: str
    ) -> Response:
        """
        Reset user password with OTP verification
        
        Args:
            email: User's email address
            otp: 4-digit OTP code
            new_password: New password
            confirm_password: Confirm password (must match new_password)
            
        Returns:
            Response indicating success or failure
        """
        # Validate required fields
        if not email or (isinstance(email, str) and not email.strip()):
            return self.response.validation_error_response("Email is required")
        
        if not otp or (isinstance(otp, str) and not otp.strip()):
            return self.response.validation_error_response("OTP is required")
        
        if not new_password or (isinstance(new_password, str) and not new_password.strip()):
            return self.response.validation_error_response("New password is required")
        
        if not confirm_password or (isinstance(confirm_password, str) and not confirm_password.strip()):
            return self.response.validation_error_response("Confirm password is required")
        
        email = email.strip().lower()
        otp = otp.strip()
        new_password = new_password.strip()
        confirm_password = confirm_password.strip()
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return self.response.validation_error_response("Invalid email format")
        
        # Validate OTP format (4 digits)
        if not re.match(r'^\d{4}$', otp):
            return self.response.validation_error_response("OTP must be a 4-digit code")
        
        # Validate passwords match
        if new_password != confirm_password:
            return self.response.passwords_do_not_match_response()
        
        # Validate password strength (minimum 8 characters)
        if len(new_password) < 8:
            return self.response.validation_error_response("Password must be at least 8 characters long")
        
        # Get user by email
        user = self.storage.get_user_by_email(email)
        if not user:
            return self.response.user_not_found_response()
        
        # Check if user uses email authentication (not GOOGLE only)
        if user.auth_provider == AuthProviderChoices.GOOGLE:
            return self.response.validation_error_response(
                "Password reset is not available for Google sign-in accounts. Please use Google sign-in to access your account."
            )
        
        # Check if OTP exists
        if not user.email_verification_otp:
            return self.response.invalid_otp_response()
        
        # Check if OTP is expired
        if user.otp_expiry and user.otp_expiry < timezone.now():
            return self.response.expired_otp_response()
        
        # Verify OTP matches
        if user.email_verification_otp != otp:
            return self.response.invalid_otp_response()
        
        try:
            # Update password
            user = self.storage.update_user_password(user, new_password)
            
            # Clear OTP fields after successful password reset
            user = self.storage.clear_password_reset_otp(user)
            
            return self.response.password_reset_success_response()
            
        except Exception as e:
            logger.error(f"Error resetting password for user {email}: {str(e)}")
            return self.response.internal_error_response(f"Failed to reset password: {str(e)}")

