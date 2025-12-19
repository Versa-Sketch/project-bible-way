from rest_framework.response import Response
from rest_framework import status


class ResendVerificationEmailResponse:
    
    @staticmethod
    def email_sent_success_response() -> Response:
        return Response(
            {
                "success": True,
                "message": "Verification email sent successfully. Please check your email."
            },
            status=status.HTTP_200_OK
        )
    
    @staticmethod
    def email_already_verified_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Email is already verified",
                "error_code": "EMAIL_ALREADY_VERIFIED"
            },
            status=status.HTTP_400_BAD_REQUEST
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

