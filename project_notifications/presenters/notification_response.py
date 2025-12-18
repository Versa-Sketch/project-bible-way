from typing import Dict, Any
from project_notifications.models import Notification


class NotificationResponse:
    """Formats notifications for WebSocket delivery."""
    
    def _get_actor_data(self, notification: Notification) -> Dict[str, Any] | None:
        """Extract actor data from notification."""
        if not notification.actor:
            return None
        return {
            'user_id': str(notification.actor.user_id),
            'user_name': notification.actor.username,
            'profile_picture_url': notification.actor.profile_picture_url or ''
        }
    
    def format_notification(self, notification: Notification) -> Dict[str, Any]:
        """Format a single notification for WebSocket."""
        # Get formatted message based on type
        message = self._get_notification_message(notification)
        
        return {
            'type': 'notification',
            'notification_id': str(notification.notification_id),
            'notification_type': notification.notification_type,
            'message': message,
            'target_id': notification.target_id,
            'target_type': notification.target_type,
            'actor': self._get_actor_data(notification),
            'metadata': notification.metadata or {},
            'created_at': notification.created_at.isoformat()
        }
    
    def format_aggregated_notification(self, notification: Notification) -> Dict[str, Any]:
        """Format an aggregated notification for WebSocket."""
        metadata = notification.metadata or {}
        actors_count = metadata.get('actors_count', 1)
        last_actor_name = metadata.get('last_actor_name', '')
        
        # Get formatted message with aggregation
        message = self._get_aggregated_message(notification, actors_count, last_actor_name)
        
        return {
            'type': 'notification',
            'notification_id': str(notification.notification_id),
            'notification_type': notification.notification_type,
            'message': message,
            'target_id': notification.target_id,
            'target_type': notification.target_type,
            'actor': self._get_actor_data(notification),
            'metadata': {
                **metadata,
                'is_aggregated': True
            },
            'created_at': notification.created_at.isoformat()
        }
    
    def _get_notification_message(self, notification: Notification) -> str:
        """Get notification message based on type."""
        actor_name = notification.actor.username if notification.actor else 'Someone'
        
        messages = {
            'FOLLOW': f"{actor_name} started following you",
            'POST_LIKE': f"{actor_name} liked your post",
            'COMMENT_LIKE': f"{actor_name} liked your comment",
            'PRAYER_REQUEST_LIKE': f"{actor_name} liked your prayer request",
            'COMMENT_ON_POST': f"{actor_name} commented on your post",
            'COMMENT_ON_PRAYER_REQUEST': f"{actor_name} commented on your prayer request",
            'PRAYER_REQUEST_CREATED': f"{actor_name} created a prayer request",
        }
        
        return messages.get(notification.notification_type, f"{actor_name} performed an action")
    
    def _get_aggregated_message(
        self,
        notification: Notification,
        actors_count: int,
        last_actor_name: str
    ) -> str:
        """Get aggregated notification message."""
        if actors_count == 1:
            return self._get_notification_message(notification)
        
        messages = {
            'POST_LIKE': self._format_like_message(actors_count, last_actor_name, 'post'),
            'COMMENT_LIKE': self._format_like_message(actors_count, last_actor_name, 'comment'),
            'PRAYER_REQUEST_LIKE': self._format_like_message(actors_count, last_actor_name, 'prayer request'),
            'COMMENT_ON_POST': self._format_comment_message(actors_count, last_actor_name, 'post'),
            'COMMENT_ON_PRAYER_REQUEST': self._format_comment_message(actors_count, last_actor_name, 'prayer request'),
        }
        
        return messages.get(notification.notification_type, f"{actors_count} people performed an action")
    
    def _format_like_message(self, count: int, last_actor: str, target: str) -> str:
        """Format aggregated like message."""
        if count == 1:
            return f"{last_actor} liked your {target}"
        elif count == 2:
            return f"{last_actor} and 1 other liked your {target}"
        else:
            return f"{last_actor} and {count - 1} others liked your {target}"
    
    def _format_comment_message(self, count: int, last_actor: str, target: str) -> str:
        """Format aggregated comment message."""
        if count == 1:
            return f"{last_actor} commented on your {target}"
        elif count == 2:
            return f"{last_actor} and 1 other commented on your {target}"
        else:
            return f"{last_actor} and {count - 1} others commented on your {target}"

