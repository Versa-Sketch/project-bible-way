from rest_framework.response import Response
from rest_framework import status


class DeletePrayerRequestResponse:

    @staticmethod
    def prayer_request_deleted_successfully_response() -> Response:
        return Response(
            {
                "success": True,
                "message": "Prayer request deleted successfully"
            },
            status=status.HTTP_200_OK
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
    def unauthorized_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "You are not authorized to delete this prayer request",
                "error_code": "UNAUTHORIZED"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    @staticmethod
    def error_response(error_message: str) -> Response:
        return Response(
            {
                "success": False,
                "error": error_message,
                "error_code": "ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

