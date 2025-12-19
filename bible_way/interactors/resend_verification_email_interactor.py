from bible_way.storage import UserDB
from bible_way.presenters.resend_verification_email_response import ResendVerificationEmailResponse
from bible_way.utils.otp_generator import generate_otp, get_otp_expiry
from bible_way.utils.email_service import ZeptoMailService
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


class ResendVerificationEmailInteractor:
    def __init__(self, storage: UserDB, response: ResendVerificationEmailResponse):
        self.storage = storage
        self.response = response
    
    def resend_verification_email_interactor(self, email: str) -> Response:
        """
        Resend verification email with new OTP
        
        Args:
            email: User's email address
            
        Returns:
            Response indicating success or failure
        """
        # Get user by email
        user = self.storage.get_user_by_email(email)
        if not user:
            return self.response.user_not_found_response()
        
        # Check if email is already verified
        if user.is_email_verified:
            return self.response.email_already_verified_response()
        
        # Generate new OTP
        otp = generate_otp()
        otp_expiry = get_otp_expiry()
        
        # Update user with new OTP
        user = self.storage.update_user_otp(user, otp, otp_expiry)
        
        # Send verification email
        email_service = ZeptoMailService()
        email_sent, email_message = email_service.send_verification_email(
            user_email=email,
            user_name=user.username,
            otp=otp
        )
        
        if not email_sent:
            logger.error(f"Failed to resend verification email to {email}: {email_message}")
            # Still return success to prevent email enumeration
            # Log the error for debugging
        
        return self.response.email_sent_success_response()

