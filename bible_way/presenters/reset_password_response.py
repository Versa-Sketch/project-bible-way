from rest_framework.response import Response
from rest_framework import status


class ResetPasswordResponse:
    
    @staticmethod
    def password_reset_success_response() -> Response:
        return Response(
            {
                "success": True,
                "message": "Password has been reset successfully. You can now login with your new password."
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
    def invalid_otp_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Invalid OTP code. Please check and try again.",
                "error_code": "INVALID_OTP"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def expired_otp_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "OTP code has expired. Please request a new password reset.",
                "error_code": "OTP_EXPIRED"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def passwords_do_not_match_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "New password and confirm password do not match.",
                "error_code": "PASSWORDS_DO_NOT_MATCH"
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
    def internal_error_response(error_message: str = None) -> Response:
        message = error_message or "An error occurred while resetting password. Please try again later."
        return Response(
            {
                "success": False,
                "error": message,
                "error_code": "INTERNAL_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

