"""
HTTP views for notification operations.

Handles notification retrieval via REST API endpoint.
"""
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from project_notifications.storage import NotificationDB
from project_notifications.interactors.get_notifications_interactor import GetNotificationsInteractor
from project_notifications.presenters.get_notifications_response import GetNotificationsResponse
from project_notifications.presenters.notification_error_response import NotificationErrorResponse


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_notifications_view(request):
    """
    Get notifications for current user based on last fetch time.
    
    GET /api/notifications/
    - First call: Returns all notifications
    - Subsequent calls: Returns only notifications created after last fetch time
    - Automatically updates last fetch time after returning notifications
    """
    user_id = str(request.user.user_id)
    
    response = GetNotificationsInteractor(
        storage=NotificationDB(),
        response=GetNotificationsResponse(),
        error_response=NotificationErrorResponse()
    ).get_notifications_interactor(user_id=user_id)
    return response
