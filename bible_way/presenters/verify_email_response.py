from rest_framework.response import Response
from rest_framework import status
from bible_way.storage.dtos import LoginResponseDTO


class VerifyEmailResponse:
    
    @staticmethod
    def verification_success_response(response_dto: LoginResponseDTO) -> Response:
        return Response(
            {
                "success": True,
                "message": "Email verified successfully",
                "access_token": response_dto.access_token,
                "refresh_token": response_dto.refresh_token
            },
            status=status.HTTP_200_OK
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
                "error": "OTP code has expired. Please request a new verification code.",
                "error_code": "OTP_EXPIRED"
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

