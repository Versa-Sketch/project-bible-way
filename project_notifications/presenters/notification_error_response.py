"""
Common error response presenter for notifications.
"""
from rest_framework.response import Response
from rest_framework import status


class NotificationErrorResponse:
    """Common error response methods for notifications."""
    
    @staticmethod
    def server_error(error_message: str = "Internal server error") -> Response:
        """Return server error response."""
        return Response(
            {
                "success": False,
                "error": error_message,
                "error_code": "SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @staticmethod
    def validation_error(error_message: str) -> Response:
        """Return validation error response."""
        return Response(
            {
                "success": False,
                "error": error_message,
                "error_code": "VALIDATION_ERROR"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
