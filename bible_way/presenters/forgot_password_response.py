from rest_framework.response import Response
from rest_framework import status


class ForgotPasswordResponse:
    
    @staticmethod
    def otp_sent_success_response() -> Response:
        return Response(
            {
                "success": True,
                "message": "Password reset OTP has been sent to your email address. Please check your inbox."
            },
            status=status.HTTP_200_OK
        )
    
    @staticmethod
    def user_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "User not found",
                "error_code": "USER_NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def invalid_auth_provider_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Password reset is not available for Google sign-in accounts. Please use Google sign-in to access your account.",
                "error_code": "INVALID_AUTH_PROVIDER"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def validation_error_response(error_message: str) -> Response:
        return Response(
            {
                "success": False,
                "error": error_message,
                "error_code": "VALIDATION_ERROR"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def email_sending_failed_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Failed to send password reset email. Please try again later.",
                "error_code": "EMAIL_SENDING_FAILED"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @staticmethod
    def email_not_verified_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Email address is not verified. Please verify your email before requesting a password reset.",
                "error_code": "EMAIL_NOT_VERIFIED"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

