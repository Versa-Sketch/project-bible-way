from rest_framework.response import Response
from rest_framework import status
from bible_way.storage.dtos import LoginResponseDTO


class LoginResponse:
    
    @staticmethod
    def invalid_credentials_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Invalid email or password",
                "error_code": "INVALID_CREDENTIALS"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def google_account_login_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "This account was created with Google. Please sign in with Google instead.",
                "error_code": "GOOGLE_ACCOUNT_LOGIN"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    @staticmethod
    def login_success_response(response_dto: LoginResponseDTO) -> Response:
        return Response(
            {
                "success": True,
                "message": "Login successful",
                "access_token": response_dto.access_token,
                "refresh_token": response_dto.refresh_token
            },
            status=status.HTTP_200_OK
        )

