"""
Interactor for fetching user notifications.
"""
from datetime import datetime
from django.utils import timezone
from rest_framework.response import Response
from project_notifications.storage import NotificationDB
from project_notifications.presenters.get_notifications_response import GetNotificationsResponse
from project_notifications.presenters.notification_error_response import NotificationErrorResponse


class GetNotificationsInteractor:
    """Interactor for getting user notifications."""
    
    def __init__(
        self,
        storage: NotificationDB,
        response: GetNotificationsResponse,
        error_response: NotificationErrorResponse
    ):
        self.storage = storage
        self.response = response
        self.error_response = error_response
    
    def get_notifications_interactor(
        self,
        user_id: str
    ) -> Response:
        """
        Get notifications for a user based on last fetch time.
        
        Args:
            user_id: ID of the user
        """
        try:
            # Get or create fetch tracker for user
            tracker = self.storage.get_or_create_fetch_tracker(user_id)
            if not tracker:
                return self.error_response.server_error("Failed to get fetch tracker")
            
            # Get last fetch time (None on first call)
            last_fetch_time = tracker.last_fetch_at
            
            # Get notifications from storage
            notifications, total_count = self.storage.get_user_notifications(
                user_id=user_id,
                last_fetch_time=last_fetch_time
            )
            
            # Update fetch tracker with current timestamp
            current_time = timezone.now()
            self.storage.update_fetch_tracker(user_id, current_time)
            
            # Format notifications
            notifications_data = []
            for notification in notifications:
                metadata = notification.metadata or {}
                actors_count = metadata.get('actors_count', 1)
                actors = metadata.get('actors', [])
                last_actor_id = metadata.get('last_actor_id', str(notification.actor.user_id) if notification.actor else None)
                
                # Get actor info (use last actor for aggregated notifications)
                actor_data = None
                if notification.actor:
                    actor_data = {
                        'user_id': str(notification.actor.user_id),
                        'user_name': notification.actor.user_name,
                        'profile_picture_url': notification.actor.profile_picture_url or ''
                    }
                
                notification_data = {
                    'notification_id': str(notification.notification_id),
                    'type': notification.notification_type,
                    'actor': actor_data,
                    'actors_count': actors_count,
                    'actors': actors,
                    'target_id': notification.target_id,
                    'target_type': notification.target_type,
                    'conversation_id': notification.conversation_id,
                    'message_id': notification.message_id,
                    'created_at': notification.created_at.isoformat() if notification.created_at else None,
                    'metadata': metadata
                }
                notifications_data.append(notification_data)
            
            return self.response.get_notifications_success_response(
                notifications=notifications_data,
                total_count=total_count
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in get_notifications_interactor: {e}")
            return self.error_response.server_error(str(e))
