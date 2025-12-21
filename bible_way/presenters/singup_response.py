from rest_framework.response import Response
from rest_framework import status
from bible_way.storage.dtos import SignupResponseDTO

class SignupResponse:
    
    @staticmethod
    def user_email_exists_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "An account with this email already exists. Please use a different email or try signing in instead.",
                "error_code": "USER_EMAIL_ALREADY_EXISTS"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    @staticmethod
    def user_username_exists_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "An account with this username already exists. Please use a different username instead.",
                "error_code": "USER_USERNAME_ALREADY_EXISTS"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def google_account_exists_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "An account with this email already exists using Google authentication. Please sign in with Google instead.",
                "error_code": "GOOGLE_ACCOUNT_EXISTS"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
                
    @staticmethod
    def account_already_linked_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "An account with this email already exists and is linked to both email/password and Google authentication.",
                "error_code": "ACCOUNT_ALREADY_LINKED"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def password_does_not_match() -> Response:
        return Response(
            {
                "success": False,
                "error": "Password does not match",
                "error_code": "PASSWORD_MISMATCH"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def missing_full_name_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "full_name is required",
                "error_code": "MISSING_FULL_NAME"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def internal_server_error_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "An unexpected error occurred. Please try again later.",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @staticmethod
    def user_signup_success_response(response_dto: SignupResponseDTO) -> Response:
        return Response(
            {
                "success": True,
                "message": "Signup successful",
                "access_token": response_dto.access_token,
                "refresh_token": response_dto.refresh_token
            },
            status=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def email_verification_required_response() -> Response:
        return Response(
            {
                "success": True,
                "message": "Account created successfully. Please check your email to verify your account.",
                "error_code": "EMAIL_VERIFICATION_REQUIRED"
            },
            status=status.HTTP_201_CREATED
        )