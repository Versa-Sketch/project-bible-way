"""
Response presenter for getting notifications.
"""
from rest_framework.response import Response
from rest_framework import status
from typing import List, Dict, Any


class GetNotificationsResponse:
    """Response formatting for getting notifications."""
    
    @staticmethod
    def get_notifications_success_response(
        notifications: List[Dict[str, Any]],
        total_count: int
    ) -> Response:
        """Return successful notifications response."""
        return Response(
            {
                "success": True,
                "data": {
                    "notifications": notifications,
                    "total_count": total_count
                }
            },
            status=status.HTTP_200_OK
        )
    
    @staticmethod
    def validation_error_response(error_message: str) -> Response:
        """Return validation error response."""
        return Response(
            {
                "success": False,
                "error": error_message,
                "error_code": "VALIDATION_ERROR"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
