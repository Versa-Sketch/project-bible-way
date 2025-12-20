from rest_framework.response import Response
from rest_framework import status


class UpdateProfileResponse:

    @staticmethod
    def profile_updated_successfully_response(profile_picture_url: str = None) -> Response:
        response_data = {
            "success": True,
            "message": "profile_updated_successfully"
        }
        if profile_picture_url:
            response_data["profile_picture_url"] = profile_picture_url
        return Response(
            response_data,
            status=status.HTTP_200_OK
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
    def error_response(error_message: str) -> Response:
        return Response(
            {
                "success": False,
                "error": error_message,
                "error_code": "INTERNAL_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
