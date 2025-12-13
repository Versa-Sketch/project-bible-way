from rest_framework.response import Response
from rest_framework import status


class UnlikePrayerRequestResponse:

    @staticmethod
    def prayer_request_unliked_successfully_response() -> Response:
        return Response(
            {
                "success": True,
                "message": "Prayer request unliked successfully"
            },
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
    def prayer_request_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Prayer request not found",
                "error_code": "PRAYER_REQUEST_NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def not_liked_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "You have not liked this prayer request",
                "error_code": "NOT_LIKED"
            },
            status=status.HTTP_400_BAD_REQUEST
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

