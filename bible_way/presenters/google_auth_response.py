from rest_framework.response import Response
from rest_framework import status
from bible_way.storage.dtos import GoogleSignupResponseDTO, GoogleLoginResponseDTO

class GoogleAuthResponse:
    
    @staticmethod
    def google_user_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Google account not found. Please sign up first.",
                "error_code": "GOOGLE_USER_NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def google_signup_failed_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Google signup failed. Please try again.",
                "error_code": "GOOGLE_SIGNUP_FAILED"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def google_token_verification_failed_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Invalid Google Token. Identity could not be verified.",
                "error_code": "INVALID_GOOGLE_TOKEN"
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def google_auth_success_response(response_dto, message: str = "Authentication successful") -> Response:
        if isinstance(response_dto, GoogleSignupResponseDTO):
            return Response(
                {
                    "success": True,
                    "message": message,
                    "access_token": response_dto.access_token,
                    "refresh_token": response_dto.refresh_token
                },
                status=status.HTTP_201_CREATED
            )
        elif isinstance(response_dto, GoogleLoginResponseDTO):
            return Response(
                {
                    "success": True,
                    "message": message,
                    "access_token": response_dto.access_token,
                    "refresh_token": response_dto.refresh_token
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "success": True,
                "message": message,
                "access_token": response_dto.access_token,
                "refresh_token": response_dto.refresh_token
            },
            status=status.HTTP_200_OK
        )
    @staticmethod
    def google_auth_failed_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Google authentication failed. Please try again.",
                "error_code": "GOOGLE_AUTH_FAILED"
            },
            status=status.HTTP_401_UNAUTHORIZED
        )