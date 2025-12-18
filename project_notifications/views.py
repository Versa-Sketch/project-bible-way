"""
REST API views for notifications.

Handles fetching missed notifications and marking notifications as read.
"""

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from project_notifications.storage import NotificationDB
from project_notifications.presenters import NotificationResponse
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_missed_notifications_view(request):
    """
    Get missed unread notifications for the authenticated user.
    
    GET /api/notifications/missed/
    
    Query Parameters:
        limit (optional): Number of notifications to return (default: 50, max: 100)
    
    Returns:
        JSON response with unread notifications created after last_fetch_at
    """
    try:
        user_id = str(request.user.user_id)
        storage = NotificationDB()
        presenter = NotificationResponse()
        
        # Get limit from query params
        limit = request.query_params.get('limit', 50)
        try:
            limit = int(limit)
            if limit > 100:
                limit = 100
            if limit < 1:
                limit = 50
        except (ValueError, TypeError):
            limit = 50
        
        # Get missed unread notifications
        notifications = storage.get_missed_notifications(user_id, limit)
        
        # Format notifications
        formatted_notifications = []
        for notification in notifications:
            metadata = notification.metadata or {}
            
            # Determine if aggregated or single
            if metadata.get('actors_count', 1) > 1:
                notification_data = presenter.format_aggregated_notification(notification)
            else:
                notification_data = presenter.format_notification(notification)
            
            formatted_notifications.append(notification_data)
        
        # Update fetch tracker after successful fetch
        tracker = storage.update_fetch_tracker(user_id)
        
        return Response({
            "success": True,
            "data": {
                "notifications": formatted_notifications,
                "count": len(formatted_notifications),
                "last_fetch_at": tracker.last_fetch_at.isoformat() if tracker.last_fetch_at else None
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(
            f"Failed to get missed notifications for user {getattr(request.user, 'user_id', 'unknown')}: {str(e)}",
            exc_info=True
        )
        return Response({
            "success": False,
            "error": "An error occurred while fetching notifications",
            "error_code": "SERVER_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read_view(request):
    """
    Mark all notifications as read for the authenticated user.
    
    POST /api/notifications/markread/
    
    Returns:
        JSON response with count of notifications marked as read
    """
    try:
        user_id = str(request.user.user_id)
        storage = NotificationDB()
        
        # Mark all notifications as read
        marked_count = storage.mark_all_as_read(user_id)
        
        return Response({
            "success": True,
            "data": {
                "message": "All notifications marked as read",
                "marked_count": marked_count
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(
            f"Failed to mark notifications as read for user {getattr(request.user, 'user_id', 'unknown')}: {str(e)}",
            exc_info=True
        )
        return Response({
            "success": False,
            "error": "An error occurred while marking notifications as read",
            "error_code": "SERVER_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

